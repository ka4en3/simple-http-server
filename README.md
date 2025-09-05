# Simple HTTP Server

A simply Python implementation of HTTP server without involving high-level web frameworks. Only serves GET and HEAD methods.

## Architecture

This server uses **asynchronous architecture** based on Python's `asyncio` library. Key features:

- **Event-driven I/O**: Uses asyncio for handling multiple connections concurrently
- **Single-threaded event loop**: Each worker process runs its own event loop
- **Non-blocking I/O**: All socket operations are non-blocking
- **Efficient resource usage**: One process can handle thousands of concurrent connections
- **Automatic selector choice**: Uses epoll on Linux, IOCP on Windows, kqueue on macOS
- **TODO: Multi-process support**: Can spawn multiple worker processes for better CPU utilization
- 
### Why Asynchronous Architecture?

1. **High Performance**: No thread switching overhead
2. **Memory Efficient**: No need to allocate stack space for each connection
3. **Scalable**: Can handle C10K problem efficiently
4. **Natural fit for I/O bound operations**: HTTP servers spend most time waiting for network I/O

## Requirements

- Python 3.9+
- No external dependencies for runtime (uses only standard library)
- Development dependencies: pytest, pytest-asyncio

## Installation

### Using UV (recommended)

```bash
# Install UV package manager
pip install uv

# Clone the repository
git clone https://github.com/ka4en3/simple-http-server.git
cd simple-http-server

# Install in development mode
uv pip install -e .
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/ka4en3/simple-http-server.git
cd simple-http-server

# Install development dependencies
pip install -r requirements.txt
```

## Project Structure

```
simple-http-server/
├── httpd.py              # Main entry point
├── pyproject.toml        # Project configuration
├── README.md             # This file
├── requirements.txt      # Development dependencies
├── src/
│   ├── __init__.py
│   ├── server.py         # Core server implementation
│   ├── http_parser.py    # HTTP request parser
│   ├── http_response.py  # HTTP response builder
│   └── utils.py          # Utility functions
├── tests/
│   └── httptest.py       # Unit tests
└── static/               # Default document root
    ├── httptest/         # HTTP test suite
    ├── index.html
    └── test.html
```

## Usage

### Basic usage

Start the server with default settings:

```bash
python httpd.py
```

This will:
- Listen on port 8080
- Serve files from `./static` directory
- Use single worker process

### Advanced usage

```bash
# Custom document root
python httpd.py -r /path/to/your/files

# Multiple workers (for better performance) !!! NOT IMPLEMENTED YET!!!
python httpd.py -w 4

# Custom port
python httpd.py -p 8000

# All options combined with debug logging
python httpd.py -r ./my_site -w 8 -p 80 -d
```

### Command Line Options

- `-r, --root PATH`: Set document root directory (default: `./static`)
- `-w, --workers N`: Number of worker processes (default: 1)
- `-p, --port PORT`: Port to listen on (default: 8080)
- `-d, --debug`: Enable debug logging

## Features

### Implemented Features

- ✅ **HTTP Methods**: GET and HEAD requests
- ✅ **Status Codes**: 200 (OK), 403 (Forbidden), 404 (Not Found), 405 (Method Not Allowed)
- ✅ **File Serving**: Serves files from DOCUMENT_ROOT
- ✅ **Directory Index**: Automatically serves `index.html` for directory requests
- ✅ **HTTP Headers**: Date, Server, Content-Length, Content-Type, Connection
- ✅ **Content Types**: Correct MIME types for .html, .css, .js, .jpg, .jpeg, .png, .gif, .swf
- ✅ **URL Decoding**: Handles spaces and %XX encoded characters
- ✅ **Keep-Alive**: Supports persistent connections
- ✅ **Security**: Prevents directory traversal attacks
- ⬜ **Multi-worker**: Can scale across multiple processes

### Security Features

- Path normalization to prevent directory traversal
- Document root jail - files outside document root cannot be accessed
- Proper handling of symbolic links
- Permission checks before serving files

## Testing

### 1. HTTP Test Suite

Test compliance with HTTP specification:

```bash
pytest tests/httptest.py -v
```

### 3. Manual Browser Test

1. Start the server:
   ```bash
   python httpd.py
   ```

2. Open in browser:
   - http://localhost:8080/ - Should show index.html
   - http://localhost:8080/test.html - Should show test page
   - http://localhost:8080/nonexistent.html - Should show 404

### 4. Load Testing

#### Using Apache Bench (ab)

```bash
# Install Apache Bench if not already installed
# On Ubuntu/Debian: sudo apt-get install apache2-utils
# On Windows: Download from Apache Lounge

# Single worker test
python httpd.py
# In another terminal:
ab -n 50000 -c 100 -r http://localhost:8080/
```
### Apache Bench Results

#### Single Worker Performance
```
Server Software:        SIMPLE-HTTPServer/0.1
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        905 bytes

Concurrency Level:      100
Time taken for tests:   31.631 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      53100000 bytes
HTML transferred:       45250000 bytes
Requests per second:    1580.74 [#/sec] (mean)
Time per request:       63.262 [ms] (mean)
Time per request:       0.633 [ms] (mean, across all concurrent requests)
Transfer rate:          1639.40 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.2      0       1
Processing:    21   59   8.2     57     127
Waiting:        1   58   8.1     57     126
Total:         22   59   8.2     58     127

Percentage of the requests served within a certain time (ms)
  50%     58
  66%     59
  75%     60
  80%     60
  90%     62
  95%     66
  98%     83
  99%    111
 100%    127 (longest request)
```
## Troubleshooting

### Common Issues

**Issue**: "Address already in use" error
```bash
# Solution 1: Wait a few seconds for OS to release the port
# Solution 2: Use a different port
python httpd.py -p 8081
```

**Issue**: "Permission denied" when binding to port
```bash
# Solution: Use a port above 1024, or run with sudo (not recommended)
python httpd.py -p 8080
```

**Issue**: Cannot access server from another machine
```bash
# Check firewall settings
# On Windows: Windows Defender Firewall might block the connection
# On Linux: Check iptables/ufw settings
```
## Development

### Adding New Features

1. **New MIME Types**: Edit `MIME_TYPES` in `src/utils.py`
2. **New HTTP Methods**: Modify `handle_request` in `src/server.py`
3. **Custom Headers**: Update `HTTPResponse` in `src/http_response.py`

### Running in Development Mode

```bash
# Enable debug logging
python httpd.py -d

# Use small test directory
python httpd.py -r ./test_files -d
```

## License

MIT License © ka4en3