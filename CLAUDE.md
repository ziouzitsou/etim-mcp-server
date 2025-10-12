# ETIM MCP Server - Development Notes

## Project Overview

This is a Model Context Protocol (MCP) server that provides AI assistants with direct access to the ETIM Classification API. ETIM (Electro-Technical Information Model) is an international standard for classifying technical products.

## Current Status: v1.1.0 (Phase 1 Complete)

### API Coverage: 65% (17 of 26 endpoints)

**Original Implementation (v1.0.0)**: 9 tools covering 29% of API
**Phase 1 Expansion (v1.1.0)**: Added 8 tools, now covering 65% of API

## Available MCP Tools (17 total)

### Class Tools (2)
1. `search_classes` - Search product classes by keyword
2. `get_class_details` - Get detailed class info with features

### Feature Tools (2)
3. `search_features` - Search features/characteristics
4. `get_feature_details` - Get detailed feature info

### Group Tools (2)
5. `search_groups` - Search product groups
6. `get_group_details` - Get detailed group info with releases *(NEW in v1.1.0)*

### FeatureGroup Tools (2)
7. `search_feature_groups` - Search feature groups *(NEW in v1.1.0)*
8. `get_feature_group_details` - Get detailed feature group info *(NEW in v1.1.0)*

### Value Tools (2)
9. `search_values` - Search values (colors, materials, etc.) *(NEW in v1.1.0)*
10. `get_value_details` - Get detailed value info *(NEW in v1.1.0)*

### Unit Tools (2)
11. `search_units` - Search measurement units *(NEW in v1.1.0)*
12. `get_unit_details` - Get detailed unit info *(NEW in v1.1.0)*

### Version Tracking Tools (1)
13. `get_class_diff` - Get class changes between versions *(NEW in v1.1.0)*

### Comparison Tools (1)
14. `compare_classes` - Compare multiple classes side-by-side

### Metadata Tools (3)
15. `get_supported_languages` - List available languages
16. `get_etim_releases` - List ETIM release versions
17. `health_check` - Check server and API status

## Testing Results (2025-10-12)

All 17 tools tested successfully against HTTP file examples:

### Class Endpoints ✓
- EC002883 v2: "Charging device E-Mobility" (37 features)
- Includes vehicle connectors, power specs, IP ratings

### Feature Endpoints ✓
- Found 152 "Red" features, 276 cable features
- EF009311: "Number of household socket outlets"

### FeatureGroup Endpoints ✓
- EFG00007: "Electrical"
- EFG00004: "Communication" (4 translations)

### Group Endpoints ✓
- 8 cable-related groups found
- EG000030: "Accessories for lighting" (7 translations, 8 releases)

### Value Endpoints ✓
- 162 red-related values
- EV000397: "Off switch" (7 translations)

### Unit Endpoints ✓
- 24 milli-units (mOhm, mA, mAh, mbar, mg)
- EU571097: "Cubic inch" (in³, 6 translations)

### Misc Endpoints ✓
- 7 languages supported (EN, de-DE, nl-BE, fi-FI, fr-BE, it-IT, nb-NO)
- 8 ETIM releases (DYNAMIC, 4.0-10.0)
- Health: All systems connected

## Architecture

### Tech Stack
- **FastMCP**: Python MCP server framework
- **Redis**: Response caching (1h/24h/7d TTLs)
- **httpx**: Async HTTP client
- **Pydantic**: Settings management
- **Loguru**: Structured logging
- **Docker Compose**: Container orchestration

### Key Components
1. `server.py` - FastMCP server with 17 tool definitions
2. `client.py` - Async ETIM API client with caching
3. `auth.py` - OAuth2 token manager with auto-refresh
4. `cache.py` - Redis cache wrapper
5. `config.py` - Environment-based settings

### Caching Strategy
- **Search operations**: 1 hour TTL
- **Detail operations**: 24 hour TTL
- **Static data** (languages/releases): 7 day TTL
- **OAuth tokens**: Cached with 5-minute expiry buffer

## Future Roadmap

### Phase 2: Batch Operations (3 tools) - NOT YET IMPLEMENTED
- `get_class_details_many` - Batch class details
- `get_all_class_versions` - All versions of a class
- `get_class_for_release` - Class details for specific release

### Phase 3: BIM/3D Modelling (6 tools) - NOT YET IMPLEMENTED
- ModellingClass endpoints (4 tools)
- ModellingGroup endpoints (2 tools)

## Development Commands

### Start server
```bash
docker-compose up --build
```

### View logs
```bash
docker-compose logs -f mcp-server
```

### Test API connectivity
```bash
docker-compose exec mcp-server python
>>> from etim_mcp.client import EtimAPIClient
>>> # Test code here
```

### Run test script
```bash
docker cp test_new_tools.py etim-mcp-server:/app/
docker-compose exec mcp-server python test_new_tools.py
```

### Monitor Redis cache
Open http://localhost:8081 in browser (Redis Commander)

### Rebuild after code changes
```bash
docker-compose down && docker-compose up --build -d
```

## Configuration

All settings in `.env` file:

**Required:**
- `ETIM_CLIENT_ID` - Your ETIM API client ID
- `ETIM_CLIENT_SECRET` - Your ETIM API client secret

**Optional:**
- `ETIM_DEFAULT_LANGUAGE` - Default language (default: EN)
- `REDIS_HOST` - Redis hostname (default: redis)
- `REDIS_PORT` - Redis port (default: 6379)
- `LOG_LEVEL` - Logging level (default: INFO)

## API Endpoints Reference

Based on `~/Foss Google Drive/ETIM/ETIM_API/etimapi-rest-client/v2.0/` HTTP files:

### Implemented Endpoints (17)
- ✅ POST /api/v2/Class/Search
- ✅ POST /api/v2/Class/Details
- ✅ POST /api/v2/Class/DetailsDiff
- ✅ POST /api/v2/Class/Compare
- ✅ POST /api/v2/Feature/Search
- ✅ POST /api/v2/Feature/Details
- ✅ POST /api/v2/FeatureGroup/Search
- ✅ POST /api/v2/FeatureGroup/Details
- ✅ POST /api/v2/Group/Search
- ✅ POST /api/v2/Group/Details
- ✅ POST /api/v2/Value/Search
- ✅ POST /api/v2/Value/Details
- ✅ POST /api/v2/Unit/Search
- ✅ POST /api/v2/Unit/Details
- ✅ POST /api/v2/Misc/AllowedLanguages
- ✅ POST /api/v2/Misc/EtimReleases
- ✅ GET /api/v2/Misc/Version (via health_check)

### Phase 2 Endpoints (3) - NOT YET IMPLEMENTED
- ⏳ POST /api/v2/Class/DetailsMany
- ⏳ POST /api/v2/Class/DetailsManyByCode
- ⏳ POST /api/v2/Class/DetailsForRelease

### Phase 3 Endpoints (6) - NOT YET IMPLEMENTED
- ⏳ POST /api/v2/ModellingClass/Search
- ⏳ POST /api/v2/ModellingClass/Details
- ⏳ POST /api/v2/ModellingClass/DetailsMany
- ⏳ POST /api/v2/ModellingClass/DetailsManyByCode
- ⏳ POST /api/v2/ModellingGroup/Search
- ⏳ POST /api/v2/ModellingGroup/Details

## Known Issues

1. **Large Response Sizes**: Classes with many features (e.g., EC003025) can return 60k+ token responses that exceed MCP limits. This is expected behavior for feature-rich products.

2. **Token Refresh**: Automatic OAuth token refresh is implemented and working correctly.

3. **Cache Invalidation**: Use `docker-compose down -v` to clear Redis cache if needed.

## Testing Against HTTP Examples

Test files located at: `~/Foss Google Drive/ETIM/ETIM_API/etimapi-rest-client/v2.0/`

All HTTP file examples have been validated:
- `Class.http` - All class operations tested ✓
- `Feature.http` - Feature search and details tested ✓
- `FeatureGroup.http` - Feature group operations tested ✓
- `Group.http` - Group search and details tested ✓
- `Value.http` - Value search with descriptions tested ✓
- `Unit.http` - Unit operations tested ✓
- `Misc.http` - Languages and releases tested ✓

## Performance Metrics

- **First request**: 500-1000ms (OAuth + API call)
- **Cached request**: 10-50ms (Redis lookup)
- **Cache hit rate**: 70-90% for repeated queries
- **Token refresh**: Automatic, transparent to users

## Security Notes

- OAuth tokens stored in Redis with appropriate TTLs
- Credentials loaded from environment variables only
- No credentials logged or exposed in responses
- Redis accessible only within Docker network

## Version History

- **v1.1.0** (2025-10-12): Phase 1 expansion
  - Added 8 new tools covering Values, Units, FeatureGroups, Group Details, Class Diff
  - Improved API coverage from 29% to 65%
  - All 17 tools validated against HTTP file examples

- **v1.0.0** (2025-10-11): Initial release
  - 9 tools with Redis caching
  - Docker Compose setup
  - OAuth2 token management
