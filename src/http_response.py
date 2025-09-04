"""
HTTP response builder
"""

from datetime import datetime
from typing import Dict, Optional


class HTTPResponse:
    """HTTP Response builder"""

    STATUS_MESSAGES = {
        200: "OK",
        400: "Bad Request",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error"
    }

    def __init__(self, status_code: int, status_message: Optional[str] = None):
        self.status_code = status_code
        self.status_message = status_message or self.STATUS_MESSAGES.get(status_code, "Unknown")
        self.headers: Dict[str, str] = {}
        self.body: Optional[bytes] = None

        # Set default headers
        self.add_header('Server', 'OTUS-HTTPServer/0.1')
        self.add_header('Date', self._format_date())
        self.add_header('Connection', 'keep-alive')

    def add_header(self, name: str, value: str):
        """Add response header"""
        self.headers[name] = value

    def to_bytes(self) -> bytes:
        """Convert response to bytes"""
        # Build status line
        status_line = f"HTTP/1.1 {self.status_code} {self.status_message}"

        # Build headers
        header_lines = [status_line]
        for name, value in self.headers.items():
            header_lines.append(f"{name}: {value}")

        # Add content length if body exists
        if self.body:
            if 'Content-Length' not in self.headers:
                self.add_header('Content-Length', str(len(self.body)))
        else:
            # For error responses without body
            if self.status_code >= 400 and 'Content-Length' not in self.headers:
                error_body = f"<html><body><h1>{self.status_code} {self.status_message}</h1></body></html>"
                self.body = error_body.encode('utf-8')
                self.add_header('Content-Length', str(len(self.body)))
                self.add_header('Content-Type', 'text/html')

        # Join headers
        headers = '\r\n'.join(header_lines) + '\r\n\r\n'

        # Combine headers and body
        response = headers.encode('utf-8')
        if self.body:
            response += self.body

        return response

    def _format_date(self) -> str:
        """Format current date for HTTP header"""
        # HTTP date format: Wed, 09 Jun 2021 10:18:14 GMT
        now = datetime.utcnow()
        weekday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][now.weekday()]
        month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][now.month - 1]
        return f"{weekday}, {now.day:02d} {month} {now.year} {now.hour:02d}:{now.minute:02d}:{now.second:02d} GMT"