#!/usr/bin/env python
"""
HTTP Server entry point
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from src.server import HTTPServer


def setup_logging(debug=False):
    """Configure logging for the server"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Simple HTTP Server')
    parser.add_argument(
        '-r', '--root',
        type=str,
        default='./static',
        help='Document root directory (default: ./static)'
    )
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=80,
        help='Port to listen on (default: 80)'
    )
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    setup_logging(args.debug)

    # Validate document root
    document_root = Path(args.root).resolve()
    if not document_root.exists():
        logging.error(f"Document root does not exist: {document_root}")
        sys.exit(1)

    if not document_root.is_dir():
        logging.error(f"Document root is not a directory: {document_root}")
        sys.exit(1)

    logging.info(f"Starting HTTP server on port {args.port}")
    logging.info(f"Document root: {document_root}")
    logging.info(f"Workers: {args.workers}")
    if args.workers != 1:
        # Multi-process mode
        logging.warning(f"Warning: Multi-worker mode is not implemented yet.")

    # Start single process mode
    server = HTTPServer(port=args.port, document_root=str(document_root))
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logging.info("Server shutting down...")
        asyncio.run(server.stop())


if __name__ == '__main__':
    main()
