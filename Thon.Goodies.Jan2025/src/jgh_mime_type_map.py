"""
jgh_mime_type_map.py

A utility module for mapping between file extensions and MIME types, ported from MimeTypeMap.cs.
Provides bidirectional lookup: extension-to-MIME and MIME-to-extension, as well as extraction of file extensions from paths.

Functions:
- get_mime_type(extension): Returns the MIME type for a given file extension.
- get_extension(mime_type, throw_error_if_not_found=True): Returns the file extension for a given MIME type.
- get_extension_from_name(name): Returns the file extension from a filename.

All lookups are case-insensitive. If a mapping is not found, sensible defaults or exceptions are used.
"""
import logging
import os
logger = logging.getLogger(__name__)


_EXT_TO_MIME = {
    # Images
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".bmp": "image/bmp",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",

    # Documents
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".txt": "text/plain",
    ".csv": "text/csv",
    ".rtf": "application/rtf",
    ".json": "application/json",
    ".xml": "application/xml",
    ".html": "text/html",
    ".htm": "text/html",

    # Archives
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".rar": "application/x-rar-compressed",
    ".7z": "application/x-7z-compressed",

    # Audio
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",

    # Video
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".wmv": "video/x-ms-wmv",
    ".webm": "video/webm",
    ".mkv": "video/x-matroska",

    # Code/Text
    ".js": "application/javascript",
    ".css": "text/css",
    ".md": "text/markdown",
}

# Add reverse mapping: mime type -> extension (if not already present)
_MIME_TO_EXT: dict[str, str] = {}
for ext, mime in _EXT_TO_MIME.items():
    if mime not in _MIME_TO_EXT:
        _MIME_TO_EXT[mime] = ext

def get_mime_type(extension: str) -> str:
   """
    Returns the MIME type for a given file extension.

    Parameters:
        extension (str): The file extension (with or without leading dot, e.g. '.jpg' or 'jpg').

    Returns:
        str: The corresponding MIME type if found, otherwise 'application/octet-stream'.

    Example:
        >>> get_mime_type('.jpg')
        'image/jpeg'
        >>> get_mime_type('unknownext')
        'application/octet-stream'
    """
   if not extension.startswith("."):
        extension = "." + extension
   return _EXT_TO_MIME.get(extension.lower(), "application/octet-stream")

def get_extension(mime_type: str, throw_error_if_not_found: bool = True) -> str:
    """
    Returns the file extension for a given MIME type.

    Parameters:
        mime_type (str): The MIME type string (e.g. 'image/jpeg').
        throw_error_if_not_found (bool): If True, raises ValueError if the MIME type is not registered.
                                        If False, returns an empty string for unknown MIME types.

    Returns:
        str: The corresponding file extension (with leading dot, e.g. '.jpg').

    Raises:
        ValueError: If the MIME type is not registered and throw_error_if_not_found is True.

    Example:
        >>> get_extension('image/jpeg')
        '.jpg'
        >>> get_extension('unknown/type', throw_error_if_not_found=False)
        ''
    """
    ext = _MIME_TO_EXT.get(mime_type.lower())
    if ext is None:
        if throw_error_if_not_found:
            raise ValueError(f"Requested mime type is not registered: {mime_type}")
        return ""
    return ext

def get_extension_from_name(name: str) -> str:
    """
    Extracts and returns the file extension from a filename.

    Parameters:
        name (str): The filename or path (e.g. 'photo.jpg', '/tmp/archive.tar.gz').

    Returns:
        str: The file extension (including the leading dot), or an empty string if none is found.

    Example:
        >>> get_extension_from_name('photo.jpg')
        '.jpg'
        >>> get_extension_from_name('archive.tar.gz')
        '.gz'
        >>> get_extension_from_name('README')
        ''
    """

    return os.path.splitext(name)[1]

