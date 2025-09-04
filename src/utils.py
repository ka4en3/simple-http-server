"""
Utility functions for HTTP server
"""

import urllib.parse
from typing import Dict


# MIME types mapping
MIME_TYPES: Dict[str, str] = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.swf': 'application/x-shockwave-flash',
    '.txt': 'text/plain',
    '.json': 'application/json',
    '.xml': 'application/xml',
    '.ico': 'image/x-icon',
}


def get_content_type(extension: str) -> str:
    """Get MIME type for file extension"""
    return MIME_TYPES.get(extension.lower(), 'application/octet-stream')


def url_decode(path: str) -> str:
    """Decode URL-encoded path"""
    try:
        # Decode percent-encoded characters
        decoded = urllib.parse.unquote(path, errors='strict')
        return decoded
    except Exception as e:
        raise ValueError(f"Invalid URL encoding: {e}")