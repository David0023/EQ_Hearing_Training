"""Common Exceptions for file upload types"""

class UnsupportedFormatException(Exception):
    """File type is not supported."""

class SizeLimitException(Exception):
    """When file size is over the limit"""

class InvalidFileException(Exception):
    """When file is not valid."""