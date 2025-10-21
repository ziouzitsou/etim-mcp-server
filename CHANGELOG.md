# Changelog

All notable changes to the ETIM MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2025-10-21

### Added
- **New `features` parameter** - Enhanced feature control with 4 modes ⭐
  - `"none"` - No features returned (metadata only)
  - `"count"` - Just feature count (99% size reduction for 121 features)
  - `"summary"` - Feature code + description only (90% reduction)
  - `"full"` - Complete feature details (previous behavior)
- **New `get_class_features` tool** - Pagination support for feature-heavy classes
  - Page-based navigation (page, per_page parameters)
  - Max 100 features per page
  - Perfect for classes like EC001744 (121 features)
  - Returns pagination metadata (total_features, total_pages, has_next_page, etc.)

### Changed
- **BREAKING: `include_features` default changed from `True` to `False`**
  - Much safer for large classes - users now opt-in to features
  - Prevents accidental large responses and token limit errors
  - Old behavior available by setting `include_features=True` or `features="full"`
- Deprecated `include_features` parameter in favor of `features` mode parameter
  - `include_features` still works for backward compatibility
  - `features` parameter takes precedence when both are specified
- Enhanced all 5 class detail tools with flexible feature control:
  - `get_class_details`
  - `get_class_details_many`
  - `get_all_class_versions`
  - `get_class_for_release`
  - `compare_classes`

### Migration Guide (v1.2.x → v1.3.0)
```python
# v1.2.x - Features included by default
get_class_details("EC001744")  # Returned all 121 features

# v1.3.0 - Features excluded by default (BREAKING CHANGE)
get_class_details("EC001744")  # Returns metadata only, no features

# Migration options:
get_class_details("EC001744", include_features=True)  # Old behavior
get_class_details("EC001744", features="full")        # Recommended new syntax
get_class_details("EC001744", features="count")       # Just the count (feature_count: 121)
get_class_details("EC001744", features="summary")     # Code + description only
get_class_features("EC001744", page=1, per_page=50)   # Paginated access
```

### Performance
- **99% size reduction** with `features="count"` mode (121 features → single integer)
- **90% size reduction** with `features="summary"` mode (full objects → code+description)
- **Pagination** allows processing large feature sets in manageable chunks

## [1.2.2] - 2025-10-21

### Fixed
- **Google Vertex AI compatibility** - Resolved schema compatibility issues (#1, #2)
  - Changed filter parameters from `Optional[list[str]] = None` to `list[str] = []`
  - Changed version parameter from `Optional[int] = None` to `int = 0` with conversion logic
  - Removes `anyOf` schemas that Vertex AI rejects when using the server as a sub-agent
  - Fully backward compatible - no breaking changes

### Contributors
- @otvegg - First external contributor! Thank you for identifying the issue and providing the fix 🎉

## [1.2.1] - 2025-10-16

### Added
- **Automatic response truncation** for large classes to prevent MCP protocol failures
  - Added `max_response_tokens` parameter (default: 20000) to 6 class detail tools
  - Automatic feature removal when responses exceed token limits
  - Clear `_response_info` metadata explaining truncation with user guidance
  - Server-side logging of truncation events with feature counts

### Changed
- Enhanced class detail tools to gracefully handle feature-rich classes (e.g., EC001744 with 121 features)
- Tools now never fail due to response size - graceful degradation instead

### Fixed
- Prevents "response exceeds maximum allowed tokens" errors for classes with many features
- Classes with 100+ features no longer cause tool failures

## [1.2.0] - 2025-10-15

### Added
- **Advanced filtering for `search_classes`** - Major feature enhancement ⭐
  - `release_filter` - Filter by ETIM releases (e.g., ETIM-9.0, ETIM-10.0, DYNAMIC)
  - `group_filter` - Filter by product groups (e.g., EG000017)
  - `feature_filter` - Filter by specific features
  - `value_filter` - Filter by specific values
  - `exclude_modelling` - Exclude BIM/3D modelling classes
- `get_all_languages` tool - Retrieve all 23 ETIM languages globally (not just account-specific)
- `get_class_details_many` tool - Batch operation for retrieving multiple classes efficiently
- `get_all_class_versions` tool - Get complete version history for a class
- `get_class_for_release` tool - Query class details for specific ETIM releases
- **EXAMPLES.md** - Comprehensive usage guide with 8 verified real-world examples
- Comprehensive API coverage analysis document

### Changed
- Improved API coverage to 62.5% (20/32 endpoints)
- Enhanced caching for new batch operations
- Updated README with badges and public release preparation
- Filter test results: 1,599 cable classes → 350 with ETIM-9.0 filter (78% reduction)

### Performance
- Multiple filter combinations significantly reduce result sets
- Batch operations significantly reduce API calls
- 24-hour cache TTL for class details
- 7-day cache TTL for language data

## [1.1.0] - 2025-10-12

### Added
- `search_values` tool - Search ETIM feature values (colors, materials, etc.)
- `get_value_details` tool - Get detailed information about specific values
- `search_units` tool - Search measurement units (mm, watts, volts, etc.)
- `get_unit_details` tool - Get detailed unit information
- `search_feature_groups` tool - Search feature group categories
- `get_feature_group_details` tool - Get detailed feature group information
- `get_group_details` tool - Get detailed product group information
- `get_class_diff` tool - Track classification changes between versions

### Changed
- Enhanced API coverage from 29% to 60% (15/25 endpoints)
- Improved caching for all new endpoints
- Fixed bug where class details without features weren't returning descriptions/synonyms

### Fixed
- Class details now always include descriptions and translations regardless of include_features parameter

## [1.0.0] - 2025-10-10

### Added
- Initial release with 9 MCP tools
- `search_classes` - Search ETIM product classes
- `get_class_details` - Get detailed class information
- `search_features` - Search ETIM features
- `get_feature_details` - Get detailed feature information
- `search_groups` - Search product groups
- `get_supported_languages` - Get account-supported languages
- `get_etim_releases` - Get ETIM release versions
- `compare_classes` - Compare multiple classes side-by-side
- `health_check` - Server health monitoring

### Infrastructure
- Docker Compose setup with health checks
- Redis caching with multi-tier TTLs
- OAuth2 token management with automatic refresh
- Structured logging with Loguru
- Async/await architecture throughout
- FastMCP server implementation

### Documentation
- Comprehensive README with usage examples
- Docker Compose setup guide
- Claude Desktop integration instructions
- API documentation for all tools

## [Unreleased]

### Planned
- BIM/Modelling support (6 additional endpoints)
- Pagination for feature-heavy responses
- Field selection for response size optimization
- Additional language support based on community needs

---

## Version Guidelines

### Types of Changes
- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes

### Version Numbers
- **Major** (X.0.0) - Breaking changes
- **Minor** (1.X.0) - New features, backward compatible
- **Patch** (1.0.X) - Bug fixes, backward compatible
