BASE = '/api/v1/users'

from httpx import AsyncClient, Response
from collections.abc import AsyncGenerator
from pathlib import Path

async def upload_profile_image(
    client: AsyncGenerator[AsyncClient, None],
    image_path: Path,
    image_type: str
) -> Response:
    with image_path.open("rb") as image:
        return await client.put(
            "/api/v1/users/profile/image",
            files={"file": (image_path.name, image, image_type)},
        )