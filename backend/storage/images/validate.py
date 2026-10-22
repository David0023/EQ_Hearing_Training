# File store related rules
import warnings
from dataclasses import dataclass
from pathlib import Path
from PIL import Image, UnidentifiedImageError

MAX_IMG_SIZE: int = 5 * 1024 * 1024
MAX_PIXELS: int = 20_000_000
ALLOWED_IMG_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}

@dataclass
class ImageMetadata:
    id: str
    format: str
    extension: str
    width: int
    height: int
    size_bytes: int

class InvalidImageError(Exception):
    """Uploaded file is not an acceptable image."""

def validate_image(path: Path, size: int) -> ImageMetadata:
    if size == 0:
        raise InvalidImageError('Empty file')

    if size > MAX_IMG_SIZE:
        raise InvalidImageError('Image size larger than limit')

    try:
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error", Image.DecompressionBombWarning
            )
            with Image.open(path) as image:
                image_format = image.format

                if image_format not in ALLOWED_IMG_FORMATS:
                    raise InvalidImageError(
                        "Unsupported image format"
                    )

                width, height = image.size

                if width * height > MAX_PIXELS:
                    raise InvalidImageError(
                        "Image dimensions exceed limit"
                    )

                image.verify()

                with Image.open(path) as image:
                    image.load()
    except InvalidImageError:
        raise
    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        ValueError,
    ) as exc:
        raise InvalidImageError('Invalid/Corrupted Image') from exc

    return ImageMetadata(
        id="",
        format=image_format,
        extension=ALLOWED_IMG_FORMATS[image_format],
        width=width,
        height=height,
        size_bytes=size
    )
