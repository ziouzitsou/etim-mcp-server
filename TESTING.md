# ETIM MCP Server - Testing Guide

## Quick Start Testing

### 1. Verify Server is Running

Check that Docker containers are running:

```bash
cd /path/to/etim-mcp-server
docker-compose ps
```

Expected output: `redis`, `mcp-server`, and `redis-commander` should all be "Up"

### 2. Configure Claude Desktop

Add to your Claude Desktop config (`claude_desktop_config.json`):

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

**Note**: Use absolute paths in the configuration.

### 3. Restart Claude Desktop

Close Claude Desktop completely and restart for the MCP server configuration to take effect.

### 4. Verify Connection

After restarting, you should see ETIM tools available in Claude Desktop.

Expected tools (21 total):
- `search_classes` - Search ETIM product classes
- `get_class_details` - Get detailed class information
- `search_features` - Search features/characteristics
- `get_feature_details` - Get feature details
- `search_groups` - Search product groups
- `get_group_details` - Get group details
- `search_values` - Search values (colors, materials, etc.)
- `get_value_details` - Get value details
- `search_units` - Search measurement units
- `get_unit_details` - Get unit details
- `search_feature_groups` - Search feature groups
- `get_feature_group_details` - Get feature group details
- `get_class_diff` - Get class changes between versions
- `compare_classes` - Compare multiple classes
- `get_supported_languages` - List available languages
- `get_etim_releases` - List ETIM releases
- `get_all_languages` - Get all ETIM languages globally
- `get_class_details_many` - Batch class details
- `get_all_class_versions` - Get all versions of a class
- `get_class_for_release` - Get class for specific release
- `health_check` - Check server health

## Test Queries

Try these queries in Claude Desktop:

### Basic Search
```
Search ETIM for "cable" products
```

Expected: List of cable-related ETIM product classes

### Class Details
```
Get details for ETIM class EC001744
```

Expected: Detailed information about the Downlight/spot/floodlight class with features

### Language Support
```
What languages does ETIM support?
```

Expected: List of supported languages (depends on your ETIM account)

### Compare Classes
```
Compare ETIM classes EC001744 and EC001679
```

Expected: Side-by-side comparison of two product classes

### Batch Operations
```
Get details for ETIM classes EC001744, EC001679, and EC002883
```

Expected: Batch retrieval of multiple class details

### Version History
```
Show me all versions of ETIM class EC002883
```

Expected: Complete version history of the class

### Health Check
```
Check ETIM server health
```

Expected: Status of Redis and ETIM API connections

## Verify Caching

Run the same query twice to verify caching works:

```
Search ETIM for "LED" products
```

The second query should be significantly faster due to Redis caching.

## Monitor Cache with Redis Commander

Open http://localhost:8081 in your browser to see:
- Cached API responses
- OAuth tokens
- Cache keys and their TTLs

## Troubleshooting

### Server Not Available

If Claude Desktop shows "ETIM server not available":

1. **Check Docker Services**:
   ```bash
   docker-compose ps
   ```

2. **View Logs**:
   ```bash
   docker-compose logs mcp-server
   ```

3. **Restart Services**:
   ```bash
   docker-compose restart
   ```

### Authentication Errors

If you see OAuth or authentication errors:

1. **Verify Credentials** in `.env`:
   ```bash
   cat .env | grep ETIM_CLIENT
   ```

   Make sure `ETIM_CLIENT_ID` and `ETIM_CLIENT_SECRET` are set correctly.

2. **Test API Manually**:
   ```bash
   docker-compose exec mcp-server python -c "
   import asyncio
   from etim_mcp.config import settings
   from etim_mcp.cache import RedisCache
   from etim_mcp.auth import EtimTokenManager

   async def test():
       cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_password)
       await cache.connect()
       token_mgr = EtimTokenManager(cache)
       token = await token_mgr.get_token()
       print(f'Token obtained successfully')
       await token_mgr.close()
       await cache.close()

   asyncio.run(test())
   "
   ```

### Cache Issues

If responses seem stale or incorrect:

1. **Clear Redis Cache**:
   ```bash
   docker-compose exec redis redis-cli FLUSHALL
   ```

2. **Restart MCP Server**:
   ```bash
   docker-compose restart mcp-server
   ```

### Claude Desktop Configuration

1. **Verify Config is Valid JSON**:
   - Open your `claude_desktop_config.json` file
   - Ensure it's properly formatted JSON
   - Check that paths use forward slashes (even on Windows)

2. **Use Absolute Paths** in the configuration

3. **Restart Claude Desktop** completely (quit, not just close window)

## Expected Performance

- **First request**: 500-1000ms (OAuth + API call + cache miss)
- **Cached request**: 10-50ms (Redis lookup)
- **Token lifetime**: 1 hour (auto-refreshed)
- **Cache TTLs**:
  - Search results: 1 hour
  - Class details: 24 hours
  - Languages/releases: 7 days

## Advanced Testing

### MCP Inspector

Test the server directly using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector docker compose -f /path/to/docker-compose.yml run --rm mcp-server
```

This opens a web interface where you can:
- See all available tools
- Test each tool with custom parameters
- View request/response payloads
- Debug issues

### Monitor Real-time Logs

Watch logs in real-time:

```bash
docker-compose logs -f mcp-server
```

You should see:
- Tool invocations
- API calls with HTTP status codes
- Cache hits/misses
- Token refreshes

### Direct API Testing

Test the ETIM client directly:

```bash
docker-compose exec mcp-server python
```

Then in Python:
```python
import asyncio
from etim_mcp.client import EtimAPIClient
from etim_mcp.config import settings
from etim_mcp.cache import RedisCache
from etim_mcp.auth import EtimTokenManager

async def test():
    cache = RedisCache(settings.redis_host, settings.redis_port, settings.redis_password)
    await cache.connect()

    token_mgr = EtimTokenManager(cache)
    client = EtimAPIClient(token_mgr, cache)

    # Test search
    results = await client.search_classes("cable", "EN", max_results=5)
    print(f"Found {results['total']} cable classes")

    await client.close()
    await token_mgr.close()
    await cache.close()

asyncio.run(test())
```

## Success Criteria

✅ Claude Desktop shows ETIM tools in the tools menu
✅ Search queries return ETIM product classes
✅ Class details include features and descriptions
✅ Responses are fast on repeated queries (caching works)
✅ Health check shows all services connected
✅ Redis Commander shows cached data
✅ Batch operations work for multiple classes
✅ Version history queries return multiple versions

## Test Data

Some known ETIM classes for testing:

- **EC001744** - Downlight/spot/floodlight (121 features)
- **EC001679** - Surface-mounted luminaire (many features)
- **EC002883** - Charging device E-Mobility (37 features)
- **EC000034** - Miniature circuit breaker (multiple versions available)
- **EC003025** - Modular built-in device (feature-rich)

## Getting Help

If you encounter issues:

1. Check the [README](README.md) for setup instructions
2. Review [CONTRIBUTING](CONTRIBUTING.md) for development guidelines
3. Open an issue on [GitHub](https://github.com/ziouzitsou/etim-mcp-server/issues)

Happy testing! 🚀
