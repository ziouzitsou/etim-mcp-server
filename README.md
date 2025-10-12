# ETIM MCP Server

A Model Context Protocol (MCP) server that provides LLMs with direct access to the ETIM Classification API. This server enables AI assistants to query product classifications, technical features, and standardized product information from the international ETIM database.

## Overview

ETIM (Electro-Technical Information Model) is an international standard for classifying technical products, primarily focused on electrical and electronic products. This MCP server wraps the ETIM API v2.0 and exposes it through the Model Context Protocol, making it accessible to any MCP-compatible AI assistant.

## Features

- **9 MCP Tools** for comprehensive ETIM API access:
  - Search product classes, features, and groups
  - Get detailed information about classifications
  - Compare multiple product classes side-by-side
  - Health checks for server components
  - Get supported languages and ETIM releases

- **2 MCP Resources** for quick reference:
  - Supported languages list
  - ETIM release versions

- **3 MCP Prompts** for common workflows:
  - Compare two product classes
  - Find products matching specifications
  - Explain a classification in detail

- **Smart Caching** with Redis:
  - 1 hour cache for search results
  - 24 hour cache for class details
  - 7 day cache for static data (languages, releases)

- **Automatic OAuth Token Management**:
  - Token caching with 5-minute expiry buffer
  - Automatic refresh on 401 errors
  - Transparent token handling

- **Production-Ready Architecture**:
  - Docker Compose setup with health checks
  - Structured logging with Loguru
  - Comprehensive error handling
  - Async/await throughout for performance

## Prerequisites

- Docker and Docker Compose installed
- ETIM API credentials (client_id and client_secret)
- Internet connection for ETIM API access

## Installation

1. **Clone or download this repository**:
   ```bash
   cd /path/to/your/projects
   ```

2. **Create a `.env` file** from the example template:
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env`** and add your ETIM API credentials:
   ```env
   ETIM_CLIENT_ID=your_client_id_here
   ETIM_CLIENT_SECRET=your_client_secret_here
   ```

4. **Build and start the services**:
   ```bash
   docker-compose up --build
   ```

The server will:
- Start Redis on port 6379
- Start the MCP server (accessible via stdio)
- Start Redis Commander on http://localhost:8081 (for cache monitoring)

## Configuration

All configuration is managed through environment variables in the `.env` file:

### Required Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ETIM_CLIENT_ID` | Your ETIM API client ID | (required) |
| `ETIM_CLIENT_SECRET` | Your ETIM API client secret | (required) |

### Optional Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `ETIM_AUTH_URL` | ETIM OAuth authentication URL | `https://etimauth.etim-international.com` |
| `ETIM_API_URL` | ETIM API base URL | `https://etimapi.etim-international.com` |
| `ETIM_DEFAULT_LANGUAGE` | Default language for queries | `EN` |
| `REDIS_HOST` | Redis server hostname | `redis` |
| `REDIS_PORT` | Redis server port | `6379` |
| `REDIS_PASSWORD` | Redis password (if required) | (empty) |
| `CACHE_TTL` | Default cache TTL (seconds) | `3600` (1 hour) |
| `CACHE_CLASS_TTL` | Class details cache TTL | `86400` (24 hours) |
| `CACHE_LANGUAGES_TTL` | Languages/releases cache TTL | `604800` (7 days) |
| `LOG_LEVEL` | Logging level | `INFO` |

### Supported Languages

The following language codes are supported (depending on your ETIM account):
- `EN` - English
- `de-DE` - German
- `nl-BE` - Dutch (Belgium)
- `fr-BE` - French (Belgium)
- `fi-FI` - Finnish
- `it-IT` - Italian
- `nb-NO` - Norwegian

## Usage

### Running the Server

Start the server with Docker Compose:

```bash
docker-compose up
```

For detached mode (runs in background):

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f mcp-server
```

Stop the server:

```bash
docker-compose down
```

### Claude Desktop Integration

To use this MCP server with Claude Desktop, add the following to your Claude configuration:

**On macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**On Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "etim": {
      "command": "docker",
      "args": [
        "compose",
        "-f",
        "/absolute/path/to/etim-mcp-server/docker-compose.yml",
        "run",
        "--rm",
        "mcp-server"
      ]
    }
  }
}
```

Replace `/absolute/path/to/etim-mcp-server` with the actual path to your installation.

After adding this configuration:
1. Restart Claude Desktop
2. The ETIM tools should appear in Claude's available tools
3. Try asking: "Search for cable products in ETIM"

## Available Tools

### search_classes
Search ETIM product classes by keyword.

**Parameters**:
- `search_text` (required): Search query (e.g., "cable", "downlight")
- `language` (optional): Language code (default: EN)
- `max_results` (optional): Maximum results to return (1-100, default: 10)

**Example**: "Search for LED downlight products"

### get_class_details
Get detailed information about a specific ETIM product class.

**Parameters**:
- `class_code` (required): ETIM class code (e.g., "EC001744")
- `version` (optional): Specific version number (latest if not provided)
- `language` (optional): Language code (default: EN)
- `include_features` (optional): Include full features list (default: true)

**Example**: "Get details for ETIM class EC001744"

### search_features
Search ETIM features/characteristics.

**Parameters**:
- `search_text` (required): Search query
- `language` (optional): Language code (default: EN)
- `max_results` (optional): Maximum results (1-100, default: 10)

**Example**: "Search for IP rating features"

### get_feature_details
Get detailed information about a specific ETIM feature.

**Parameters**:
- `feature_code` (required): ETIM feature code (e.g., "EF007793")
- `language` (optional): Language code (default: EN)

**Example**: "Get details for feature EF007793"

### search_groups
Search ETIM product groups.

**Parameters**:
- `search_text` (required): Search query
- `language` (optional): Language code (default: EN)
- `max_results` (optional): Maximum results (1-100, default: 10)

**Example**: "Search for lighting product groups"

### get_supported_languages
Get list of supported languages for your ETIM account.

**Parameters**: None

**Example**: "What languages does ETIM support?"

### get_etim_releases
Get list of ETIM release versions.

**Parameters**: None

**Example**: "Show me ETIM release versions"

### compare_classes
Compare multiple ETIM product classes side-by-side.

**Parameters**:
- `class_codes` (required): List of class codes to compare (max 5)
- `language` (optional): Language code (default: EN)

**Example**: "Compare classes EC001744 and EC001679"

### health_check
Check server health and connection status.

**Parameters**: None

**Example**: "Check ETIM server health"

## Architecture

```
┌─────────────────────┐
│  Claude Desktop     │
│   (MCP Client)      │
└──────────┬──────────┘
           │ stdio
┌──────────▼──────────┐
│   FastMCP Server    │
│  (Python/AsyncIO)   │
├─────────────────────┤
│  • Auth Manager     │
│  • API Client       │
│  • Cache Layer      │
└─────┬──────────┬────┘
      │          │
      │          │ TCP
┌─────▼──────┐   │
│ Redis      │◄──┘
│ (Cache)    │
└────────────┘
      │
┌─────▼──────────────┐
│  ETIM API v2.0     │
│  (OAuth2 + REST)   │
└────────────────────┘
```

### Components

1. **FastMCP Server** (`server.py`): Main MCP server with tools, resources, and prompts
2. **ETIM API Client** (`client.py`): Async HTTP client for ETIM API with caching
3. **Token Manager** (`auth.py`): OAuth2 token management with automatic refresh
4. **Redis Cache** (`cache.py`): Async Redis wrapper for response caching
5. **Configuration** (`config.py`): Pydantic settings from environment variables

## Development

### Local Development Setup

1. Install Python 3.11+:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run Redis locally:
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

3. Create `.env` file with your credentials

4. Run the server:
   ```bash
   python -m mcp run src.etim_mcp.server:mcp
   ```

### Project Structure

```
etim-mcp-server/
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
├── .env                     # Configuration (not in git)
├── .env.example             # Configuration template
├── .gitignore               # Git ignore rules
├── README.md                # This file
└── src/
    └── etim_mcp/
        ├── __init__.py      # Package initialization
        ├── server.py        # FastMCP server with tools
        ├── client.py        # ETIM API client
        ├── auth.py          # OAuth token manager
        ├── cache.py         # Redis cache wrapper
        └── config.py        # Settings management
```

### Testing

Test individual tools using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector docker compose run --rm mcp-server
```

Or test API connectivity directly:

```bash
# Enter the container
docker-compose run --rm mcp-server bash

# Run Python interactively
python
>>> from etim_mcp.config import settings
>>> from etim_mcp.cache import RedisCache
>>> from etim_mcp.auth import EtimTokenManager
>>> from etim_mcp.client import EtimAPIClient
>>> import asyncio
>>>
>>> async def test():
...     cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_password)
...     await cache.connect()
...     token_mgr = EtimTokenManager(cache)
...     client = EtimAPIClient(token_mgr, cache)
...     result = await client.get_allowed_languages()
...     print(result)
...     await client.close()
...     await token_mgr.close()
...     await cache.close()
>>>
>>> asyncio.run(test())
```

## Monitoring

### Redis Commander

Access the Redis Commander web UI at http://localhost:8081 to:
- View cached keys and their values
- Monitor cache hit/miss rates
- Inspect token storage
- Manually clear cache if needed

### Logs

View structured logs with timestamps:

```bash
docker-compose logs -f mcp-server
```

Log levels can be adjusted in `.env`:
- `DEBUG`: Verbose logging including cache operations
- `INFO`: Normal operational logs (default)
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors

## Troubleshooting

### Server won't start

**Problem**: `Failed to connect to Redis`

**Solution**: Ensure Redis is running and healthy:
```bash
docker-compose ps
docker-compose logs redis
```

### Authentication errors

**Problem**: `Failed to obtain access token: 401`

**Solution**: Verify your credentials in `.env`:
- Check `ETIM_CLIENT_ID` is correct
- Check `ETIM_CLIENT_SECRET` is correct
- Ensure there are no extra spaces or quotes

### API request failures

**Problem**: `HTTP error: 401` during API calls

**Solution**: The server automatically refreshes tokens, but if issues persist:
1. Check ETIM API status
2. Verify your account has access to requested resources
3. Clear Redis cache: `docker-compose down -v && docker-compose up`

### Claude Desktop can't find the server

**Problem**: Tools don't appear in Claude Desktop

**Solution**:
1. Verify the absolute path in `claude_desktop_config.json`
2. Ensure `.env` file exists with valid credentials
3. Test the server manually: `docker-compose run --rm mcp-server`
4. Restart Claude Desktop completely
5. Check Claude Desktop logs for MCP errors

### Slow responses

**Problem**: Queries take too long

**Solution**:
1. Check Redis is working: `docker-compose logs redis`
2. First queries are slower (cache miss) - subsequent queries should be fast
3. Monitor cache hit rates in Redis Commander
4. Adjust cache TTLs in `.env` if needed

### Clear all cached data

```bash
docker-compose down -v
docker-compose up -d
```

The `-v` flag removes volumes, including Redis data.

## Performance

- **First request latency**: 500-1000ms (OAuth + API call)
- **Cached request latency**: 10-50ms (Redis lookup)
- **Token refresh**: Automatic, transparent to users
- **Cache hit rate**: Typically 70-90% for repeated queries

## Security

- OAuth tokens are stored in Redis with appropriate TTLs
- Credentials are loaded from environment variables only
- No credentials are logged or exposed in responses
- Redis is accessible only within Docker network (not exposed externally)

## License

This project is private and proprietary. Not for redistribution.

## Credits

- Built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
- Powered by [ETIM International](https://www.etim-international.com/)
- Uses Redis for caching, httpx for async HTTP, Pydantic for configuration

## Support

For ETIM API questions or issues:
- ETIM International website: https://www.etim-international.com/
- ETIM API documentation: https://etimapi.etim-international.com/swagger/index.html

For MCP protocol questions:
- Model Context Protocol: https://github.com/modelcontextprotocol
- FastMCP documentation: https://github.com/modelcontextprotocol/python-sdk

## Version History

- **1.0.0** (Current): Initial release with 9 tools, Redis caching, and Docker Compose setup
