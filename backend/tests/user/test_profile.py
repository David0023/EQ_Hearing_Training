import pytest
import asyncio
from pathlib import Path

from tests.user.helpers import upload_profile_image

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

async def test_profile_image_initial_upload(authenticated_client, tmp_path):
    image_key = None

    file_path = Path(__file__).parent / "assets/profile.png"
    response = await upload_profile_image(authenticated_client, file_path, 'image/png')
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
    file_path = tmp_path / "fake_profile.png"
    file_path.write_bytes(b"image bytes")

    response = await upload_profile_image(authenticated_client, file_path, 'image/png')
    assert response.status_code == 400

async def test_profile_image_upload_fails_for_file_greater_than_5mb(authenticated_client):
    file_path = Path(__file__).parent / "assets/large.jpg"

    response = await upload_profile_image(authenticated_client, file_path, 'image/jpeg')
    assert response.status_code == 413

async def test_profile_image_upload_fails_for_unsupported(authenticated_client, tmp_path):
    from PIL import Image

    file_path = tmp_path / "unsupported.gif"
    Image.new("RGB", (2, 2)).save(file_path, format="GIF")

    response = await upload_profile_image(authenticated_client, file_path, "image/gif")
    assert response.status_code == 415

async def test_profile_image_allow_public_access(authenticated_client):
    file_path = Path(__file__).parent / "assets/profile.png"
    response = await upload_profile_image(authenticated_client, file_path, 'image/png')
    assert response.status_code == 200
    assert response.json()['profile_image_key']
    image_key = response.json()['profile_image_key']

    # Remove tokens. Unauthorized
    authenticated_client.headers.pop("Authorization", None)
    authenticated_client.cookies.delete("refresh_token")
    response = await authenticated_client.get("/api/v1/users/me")
    assert response.status_code == 401

    # Image should still be accessible
    response = await authenticated_client.get(f'/uploads/{image_key}')
    assert response.status_code == 200

async def test_profile_image_update_deletes_old(authenticated_client):
    file_path = Path(__file__).parent / "assets/profile.png"

    response = await upload_profile_image(authenticated_client, file_path, 'image/png')
    assert response.status_code == 200
    old_key = response.json()['profile_image_key']

    # Check the image upload url initially
    response = await authenticated_client.get(f'/uploads/{old_key}')
    assert response.status_code == 200

    file_path = Path(__file__).parent / "assets/new_profile.jpg"
    response = await upload_profile_image(authenticated_client, file_path, 'image/jpeg')
    assert response.status_code == 200
    assert response.json()['profile_image_key']
    new_key = response.json()['profile_image_key']

    """
        *** When using ASGITransport, responses' background tasks is awaited. ***
        *** Using actual server and browswer, would not await for image deletion finishes. ***
    """
    assert new_key != old_key
    response = await authenticated_client.get(f'/uploads/{old_key}')
    assert response.status_code == 404
    response = await authenticated_client.get(f'/uploads/{new_key}')
    assert response.status_code == 200

    