"""
Asynchronous HTTP Server implementation
"""

import asyncio
import logging
import os
import socket
from pathlib import Path

from .http_parser import HTTPRequest, parse_http_request
from .http_response import HTTPResponse
from .utils import get_content_type, url_decode

logger = logging.getLogger(__name__)


class HTTPServer:
    """Asynchronous HTTP Server"""

    def __init__(self, host='0.0.0.0', port=80, document_root='./static'):
        self.host = host
        self.port = port
        self.document_root = Path(document_root).resolve()
        self.server = None
        self.clients = set()

    async def start(self):
        """Start the server"""
        # Create server with SO_REUSEADDR option
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Try to use SO_REUSEPORT if available (Linux)
        if hasattr(socket, 'SO_REUSEPORT'):
            try:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except OSError:
                logger.warning("SO_REUSEPORT not supported on this platform")

        server_socket.bind((self.host, self.port))
        server_socket.setblocking(False)

        # Create asyncio server
        self.server = await asyncio.start_server(
            self.handle_client,
            sock=server_socket,
            backlog=1024
        )

        logger.info(f"Server listening on {self.host}:{self.port}")

        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        """Stop the server"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Close all client connections
        for task in self.clients:
            task.cancel()

        if self.clients:
            await asyncio.gather(*self.clients, return_exceptions=True)

    async def handle_client(self, reader, writer):
        """Handle client connection"""
        client_address = writer.get_extra_info('peername')
        logger.debug(f"New connection from {client_address}")

        # Track this connection
        task = asyncio.current_task()
        self.clients.add(task)

        try:
            while True:
                # Read request with timeout
                try:
                    data = await asyncio.wait_for(reader.read(8192), timeout=30.0)
                except asyncio.TimeoutError:
                    logger.debug(f"Timeout reading from {client_address}")
                    break

                if not data:
                    break

                # Parse HTTP request
                try:
                    request = parse_http_request(data)
                except ValueError as e:
                    logger.error(f"Invalid request from {client_address}: {e}")
                    response = HTTPResponse(400, "Bad Request")
                    writer.write(response.to_bytes())
                    await writer.drain()
                    break

                # Handle request
                response = await self.handle_request(request)

                # Send response
                writer.write(response.to_bytes())
                await writer.drain()

                # Check if we should close connection
                if request.headers.get('Connection', '').lower() == 'close':
                    break

                # For HTTP/1.0, close unless keep-alive
                if request.version == 'HTTP/1.0' and \
                        request.headers.get('Connection', '').lower() != 'keep-alive':
                    break

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}", exc_info=True)

        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

            self.clients.discard(task)
            logger.debug(f"Connection closed for {client_address}")

    # noinspection D
    async def handle_request(self, request: HTTPRequest) -> HTTPResponse:
        """Handle HTTP request and return response"""
        # Only allow GET and HEAD methods
        if request.method not in ('GET', 'HEAD'):
            return HTTPResponse(405, "Method Not Allowed")

        # Decode and normalize path
        try:
            path = url_decode(request.path)
            logging.debug(f"Decoded path: {path}")
        except ValueError:
            return HTTPResponse(400, "Bad Request")

        # Remove query string
        if '?' in path:
            path = path.split('?')[0]

        # Prevent directory traversal
        if '../' in path:
            return HTTPResponse(403, "Forbidden")

        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]

        # check for trailing slash
        ends_with_slash = path.endswith("/")

        # Construct full file path
        file_path = self.document_root / path

        # when path ends with slash, it should be a directory
        if ends_with_slash:
            if not file_path.is_dir():
                return HTTPResponse(404, "Not Found")

        try:
            # Resolve to handle symlinks securely
            file_path = file_path.resolve()

            # Ensure file is within document root
            if not str(file_path).startswith(str(self.document_root)):
                return HTTPResponse(403, "Forbidden")

            # Check if path exists
            if not file_path.exists():
                return HTTPResponse(404, "Not Found")

            # Handle directory requests
            if file_path.is_dir():
                # Try index.html
                index_path = file_path / 'index.html'
                if index_path.exists() and index_path.is_file():
                    file_path = index_path
                else:
                    return HTTPResponse(404, "Forbidden")

            # Check if it's a regular file
            if not file_path.is_file():
                return HTTPResponse(403, "Forbidden")

            # Read file content
            try:
                content = file_path.read_bytes()
            except PermissionError:
                return HTTPResponse(403, "Forbidden")
            except Exception:
                return HTTPResponse(500, "Internal Server Error")

            # Create response
            response = HTTPResponse(200, "OK")

            # Set content type
            content_type = get_content_type(file_path.suffix)
            response.add_header('Content-Type', content_type)

            # Set content length
            response.add_header('Content-Length', str(len(content)))

            # Add body only for GET requests
            if request.method == 'GET':
                response.body = content

            return response

        except Exception as e:
            logger.error(f"Error handling request for {request.path}: {e}")
            return HTTPResponse(500, "Internal Server Error")