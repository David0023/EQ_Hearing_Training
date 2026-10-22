from uuid import uuid4
from pathlib import Path
from typing import Protocol

from storage.images.validate import (
    validate_image, InvalidImageError, MAX_IMG_SIZE, ImageMetadata
)

CHUNK_SIZE: int = 64 * 1024

# Protocol defines interface that an object must include.
class AsyncReadable(Protocol):
    # We are taking in something that has read method which retuns bytes
    async def read(self, size: int = -1) -> bytes: ...

async def upload_image(upload_dir: Path, stream: AsyncReadable) -> ImageMetadata:
    upload_dir.mkdir(parents=True, exist_ok=True)

    temp_path = upload_dir / f".{uuid4().hex}.tmp"
    final_path = None

    try:
        size = 0

        with temp_path.open("wb") as out:
            while chunk := await stream.read(CHUNK_SIZE):
                size += len(chunk)

                if size > MAX_IMG_SIZE:
                    raise InvalidImageError("Image size larger than limit")

                out.write(chunk)

        try:
            metadata = validate_image(temp_path, size)
        except InvalidImageError:
            raise

        image_id = uuid4().hex
        final_path = (
            upload_dir
            / f"{image_id}{metadata.extension}"
        )

        temp_path.replace(final_path)

        metadata.id = image_id

        return metadata

    finally:
        temp_path.unlink(missing_ok=True)

def delete_image(upload_dir: Path, storage_key: str) -> None:
    resolved_upload_dir = upload_dir.resolve()
    path = (resolved_upload_dir / storage_key).resolve()

    if not path.is_relative_to(resolved_upload_dir):
        raise ValueError("Invalid storage key")

    path.unlink(missing_ok=True)