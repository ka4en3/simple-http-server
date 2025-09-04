"""
HTTP request parser
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class HTTPRequest:
    """HTTP Request representation"""
    method: str
    path: str
    version: str
    headers: Dict[str, str]
    body: Optional[bytes] = None


def parse_http_request(data: bytes) -> HTTPRequest:
    """Parse HTTP request from raw bytes"""
    try:
        # Split headers and body
        parts = data.split(b'\r\n\r\n', 1)
        header_data = parts[0]
        body = parts[1] if len(parts) > 1 else b''

        # Parse headers
        lines = header_data.decode('utf-8', errors='ignore').split('\r\n')

        if not lines:
            raise ValueError("Empty request")

        # Parse request line
        request_line = lines[0].split(' ')
        if len(request_line) != 3:
            raise ValueError("Invalid request line")

        method, path, version = request_line

        # Validate HTTP version
        if not version.startswith('HTTP/'):
            raise ValueError("Invalid HTTP version")

        # Parse headers
        headers = {}
        for line in lines[1:]:
            if not line:
                continue

            if ':' not in line:
                raise ValueError(f"Invalid header: {line}")

            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()

        return HTTPRequest(
            method=method,
            path=path,
            version=version,
            headers=headers,
            body=body if body else None
        )

    except Exception as e:
        raise ValueError(f"Failed to parse HTTP request: {e}")