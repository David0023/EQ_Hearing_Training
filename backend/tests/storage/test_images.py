from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from storage.exceptions import InvalidFileException, SizeLimitException, UnsupportedFormatException
from storage.images.service import delete_image, upload_image
from storage.images.validate import MAX_IMG_SIZE, validate_image


def _image_bytes(format="PNG", size=(8, 6)):
    stream = BytesIO()
    Image.new("RGB", size, "blue").save(stream, format=format)
    return stream.getvalue()


class Stream:
    def __init__(self, data):
        self.data = data

    async def read(self, size=-1):
        chunk, self.data = self.data[:size], self.data[size:]
        return chunk


def test_validate_image_rejects_empty_oversize_invalid_and_unsupported(tmp_path):
    with pytest.raises(InvalidFileException):
        validate_image(tmp_path / "empty", 0)
    with pytest.raises(SizeLimitException):
        validate_image(tmp_path / "large", MAX_IMG_SIZE + 1)

    corrupt = tmp_path / "corrupt.png"
    corrupt.write_bytes(b"not an image")
    with pytest.raises(InvalidFileException):
        validate_image(corrupt, corrupt.stat().st_size)

    unsupported = tmp_path / "unsupported.bmp"
    unsupported.write_bytes(_image_bytes("BMP"))
    with pytest.raises(UnsupportedFormatException):
        validate_image(unsupported, unsupported.stat().st_size)


def test_validate_image_reports_metadata_and_limits_dimensions(tmp_path):
    path = tmp_path / "valid.png"
    path.write_bytes(_image_bytes())
    metadata = validate_image(path, path.stat().st_size)
    assert (metadata.format, metadata.extension, metadata.width, metadata.height) == ("PNG", ".png", 8, 6)

    huge = tmp_path / "huge.png"
    huge.write_bytes(_image_bytes(size=(5000, 5000)))
    with pytest.raises(SizeLimitException):
        validate_image(huge, huge.stat().st_size)


@pytest.mark.anyio
async def test_upload_and_delete_image(tmp_path):
    upload_dir = tmp_path / "uploads"
    metadata = await upload_image(upload_dir, Stream(_image_bytes()))
    stored = upload_dir / f"{metadata.id}.png"
    assert stored.is_file()
    assert not list(upload_dir.glob("*.tmp"))
    delete_image(upload_dir, stored.name)
    assert not stored.exists()
    delete_image(upload_dir, stored.name)


@pytest.mark.anyio
async def test_upload_cleans_up_when_size_limit_is_exceeded(tmp_path):
    with pytest.raises(SizeLimitException):
        await upload_image(tmp_path, Stream(b"x" * (MAX_IMG_SIZE + 1)))
    assert not list(tmp_path.iterdir())


def test_delete_image_blocks_paths_outside_upload_directory(tmp_path):
    uploads = tmp_path / "uploads"
    uploads.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"safe")
    with pytest.raises(ValueError, match="Invalid storage key"):
        delete_image(uploads, "../outside.png")
    assert outside.exists()
