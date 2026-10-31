import pytest
import asyncio
from pathlib import Path

pytestmark = pytest.mark.anyio


async def test_profile_fields(authenticated_client):
    response = await authenticated_client.get('/api/v1/users/me')
    assert response.status_code == 200
    
    body = response.json()
    assert body['username'], body['email']
    assert body['created_at'], body['updated_at']
    assert 'password' not in body
    assert 'hashed_pwd' not in body
    assert body['profile_img_key'] is None

async def test_profile_image_update(authenticated_client, tmp_path):
    image_key = None

    file_path = Path(__file__).parent / "profile.png"
    with file_path.open('rb') as f:
        response = await authenticated_client.put(
            '/api/v1/users/profile/image',
            files={'file': (file_path.name, f, 'image/png')}
        )
        assert response.status_code == 200
        assert response.json()['profile_image_key']
        image_key = response.json()['profile_image_key']

    # Check the image upload url
    image_url = f'/uploads/{image_key}'
    response = await authenticated_client.get(image_url)
    assert response.status_code == 200

    # Download the image and compare with original file
    downloaded_path = tmp_path / "downloaded.png"
    downloaded_path.write_bytes(response.content)
    assert downloaded_path.read_bytes() == file_path.read_bytes()

async def test_profile_image_upload_fails_for_invalid_content(authenticated_client, tmp_path):
    file_path = tmp_path / "profile.png"
    file_path.write_bytes(b"image bytes")

    with file_path.open('rb') as f:
        response = await authenticated_client.put(
            '/api/v1/users/profile/image',
            files={'file': (file_path.name, f, 'image/png')}
        )
        assert response.status_code == 400

async def test_profile_image_upload_fails_for_file_greater_than_5mb(authenticated_client):
    file_path = Path(__file__).parent / "large.jpg"

    with file_path.open('rb') as f:
        response = await authenticated_client.put(
            '/api/v1/users/profile/image',
            files={'file': (file_path.name, f, 'image/jpeg')}
        )
        assert response.status_code == 413