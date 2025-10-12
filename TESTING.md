# ETIM MCP Server - Testing Guide

## Quick Start

The ETIM MCP server has been configured in your Claude Desktop at:
`/mnt/c/Users/chris/AppData/Roaming/Claude/claude_desktop_config.json`

## Testing Steps

### 1. Restart Claude Desktop

Close Claude Desktop completely and restart it for the new MCP server configuration to take effect.

### 2. Verify Server Connection

After restarting Claude Desktop, you should see the ETIM tools available. Check the MCP tools section (usually shows as a hammer icon or tools menu).

Expected tools:
- search_classes
- get_class_details
- search_features
- get_feature_details
- search_groups
- get_supported_languages
- get_etim_releases
- compare_classes
- health_check

### 3. Test Queries

Try these test queries in Claude Desktop:

#### Basic Search
```
Search ETIM for "cable" products
```

Expected: Should return a list of cable-related ETIM product classes

#### Class Details
```
Get details for ETIM class EC001744
```

Expected: Should return detailed information about the Downlight/spot/floodlight class, including 121 features

#### Language Support
```
What languages does ETIM support?
```

Expected: Should return 7 languages (EN, de-DE, nl-BE, fr-BE, fi-FI, it-IT, nb-NO)

#### Compare Classes
```
Compare ETIM classes EC001744 and EC001679
```

Expected: Should return side-by-side comparison of two product classes

#### Health Check
```
Check ETIM server health
```

Expected: Should return status of Redis and ETIM API connections

### 4. Verify Caching

Run the same query twice:
```
Search ETIM for "LED" products
```

The second query should be significantly faster due to Redis caching.

### 5. Monitor with Redis Commander

Open http://localhost:8081 in your browser to see:
- Cached API responses
- OAuth tokens
- Cache keys and their TTLs

## Troubleshooting

### Server Not Available

If Claude Desktop shows "ETIM server not available":

1. **Check Docker Services**:
   ```bash
   cd "/home/sysadmin/Foss Google Drive/ETIM/ETIM_API/etim-mcp-server"
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
       print(f'Token: {token[:50]}...')
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

### Claude Desktop Not Finding Server

1. **Check Config File** is valid JSON:
   ```bash
   cat "/mnt/c/Users/chris/AppData/Roaming/Claude/claude_desktop_config.json" | python -m json.tool
   ```

2. **Ensure Absolute Path** is correct in config:
   ```
   /home/sysadmin/Foss Google Drive/ETIM/ETIM_API/etim-mcp-server/docker-compose.yml
   ```

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

### Test All Tools Programmatically

You can test the server directly using the MCP inspector:

```bash
npx @modelcontextprotocol/inspector docker compose -f "/home/sysadmin/Foss Google Drive/ETIM/ETIM_API/etim-mcp-server/docker-compose.yml" run --rm mcp-server
```

This opens a web interface where you can:
- See all available tools
- Test each tool with custom parameters
- View request/response payloads
- Debug issues

### Monitor Real-time Logs

Watch logs in real-time:

```bash
cd "/home/sysadmin/Foss Google Drive/ETIM/ETIM_API/etim-mcp-server"
docker-compose logs -f mcp-server
```

You should see:
- Tool invocations
- API calls (with HTTP status codes)
- Cache hits/misses
- Token refreshes

## Success Criteria

✅ Claude Desktop shows ETIM tools in the tools menu
✅ Search queries return ETIM product classes
✅ Class details include features and descriptions
✅ Responses are fast on repeated queries (caching works)
✅ Health check shows all services connected
✅ Redis Commander shows cached data

## Next Steps

Once testing is successful:

1. **Create workflow prompts** for common ETIM queries
2. **Add favorite classes** to your knowledge base
3. **Integrate with other tools** (e.g., use Brave search to find products, then classify with ETIM)
4. **Share feedback** on what features you'd like added

## Repository

Code: https://github.com/ziouzitsou/etim-mcp-server
Issues: https://github.com/ziouzitsou/etim-mcp-server/issues

Happy testing! 🚀
