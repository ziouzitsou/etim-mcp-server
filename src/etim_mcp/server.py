"""FastMCP server for ETIM API"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Optional
import sys
from loguru import logger

from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

from .auth import EtimTokenManager
from .cache import RedisCache
from .client import EtimAPIClient
from .config import settings


# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level=settings.log_level,
)


@dataclass
class AppContext:
    """Application context with initialized dependencies"""
    client: EtimAPIClient
    cache: RedisCache


@asynccontextmanager
async def etim_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Manage application lifecycle - startup and shutdown

    Args:
        server: FastMCP server instance

    Yields:
        AppContext with initialized dependencies
    """
    logger.info("Starting ETIM MCP Server...")

    # Startup: Initialize resources
    cache = RedisCache(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password
    )

    try:
        await cache.connect()
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

    token_manager = EtimTokenManager(cache)
    client = EtimAPIClient(token_manager, cache)

    # Test connection
    try:
        logger.info("Testing ETIM API connection...")
        if await client.test_connection():
            logger.success("ETIM API connection successful!")
        else:
            logger.warning("ETIM API connection test failed")
    except Exception as e:
        logger.error(f"Error testing connection: {e}")

    try:
        yield AppContext(client=client, cache=cache)
    finally:
        # Shutdown: Cleanup resources
        logger.info("Shutting down ETIM MCP Server...")
        await client.close()
        await token_manager.close()
        await cache.close()
        logger.info("Shutdown complete")


# Create FastMCP server instance
mcp = FastMCP(
    "ETIM Classification API",
    lifespan=etim_lifespan,
)


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
async def search_classes(
    search_text: str,
    language: str = "EN",
    max_results: int = 10,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Search ETIM product classes by keyword.

    Args:
        search_text: Search query (e.g., "cable", "downlight")
        language: Language code (EN, de-DE, nl-BE, etc.)
        max_results: Maximum number of results to return (1-100)

    Returns:
        Dictionary with 'total' count and list of matching 'classes'
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.search_classes(
            search_text=search_text,
            language=language,
            from_=0,
            size=min(max_results, 100)
        )

        return {
            "total": result.get("total", 0),
            "classes": result.get("classes", []),
            "search_text": search_text,
            "language": language
        }
    except Exception as e:
        logger.error(f"Error searching classes: {e}")
        return {"error": str(e), "total": 0, "classes": []}


@mcp.tool()
async def get_class_details(
    class_code: str,
    version: Optional[int] = None,
    language: str = "EN",
    include_features: bool = True,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get detailed information about a specific ETIM product class.

    Args:
        class_code: ETIM class code (e.g., "EC001744")
        version: Specific version number (latest if not provided)
        language: Language code (EN, de-DE, nl-BE, etc.)
        include_features: Include full list of features

    Returns:
        Detailed class information including description, features, and metadata
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_class_details(
            class_code=class_code,
            version=version,
            language=language,
            include_features=include_features
        )
        return result
    except Exception as e:
        logger.error(f"Error getting class details: {e}")
        return {"error": str(e), "code": class_code}


@mcp.tool()
async def search_features(
    search_text: str,
    language: str = "EN",
    max_results: int = 10,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Search ETIM features/characteristics.

    Args:
        search_text: Search query
        language: Language code
        max_results: Maximum number of results

    Returns:
        Dictionary with matching features
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.search_features(
            search_text=search_text,
            language=language,
            from_=0,
            size=min(max_results, 100)
        )
        return result
    except Exception as e:
        logger.error(f"Error searching features: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_feature_details(
    feature_code: str,
    language: str = "EN",
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get detailed information about a specific ETIM feature.

    Args:
        feature_code: ETIM feature code (e.g., "EF007793")
        language: Language code

    Returns:
        Feature details including type, description, and values
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_feature_details(
            feature_code=feature_code,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"Error getting feature details: {e}")
        return {"error": str(e), "code": feature_code}


@mcp.tool()
async def search_groups(
    search_text: str,
    language: str = "EN",
    max_results: int = 10,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Search ETIM product groups.

    Args:
        search_text: Search query
        language: Language code
        max_results: Maximum number of results

    Returns:
        Dictionary with matching groups
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.search_groups(
            search_text=search_text,
            language=language,
            from_=0,
            size=min(max_results, 100)
        )
        return result
    except Exception as e:
        logger.error(f"Error searching groups: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_supported_languages(
    ctx: Context[ServerSession, AppContext] = None,
) -> list:
    """
    Get list of supported languages for this ETIM account.

    Returns:
        List of language dictionaries with code and description
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_allowed_languages()
        return result
    except Exception as e:
        logger.error(f"Error getting languages: {e}")
        return []


@mcp.tool()
async def get_etim_releases(
    ctx: Context[ServerSession, AppContext] = None,
) -> list:
    """
    Get list of ETIM release versions.

    Returns:
        List of release information
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_releases()
        return result
    except Exception as e:
        logger.error(f"Error getting releases: {e}")
        return []


@mcp.tool()
async def compare_classes(
    class_codes: list[str],
    language: str = "EN",
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Compare multiple ETIM product classes side-by-side.

    Args:
        class_codes: List of class codes to compare (e.g., ["EC001744", "EC001679"])
        language: Language code

    Returns:
        Dictionary with comparison data for all classes
    """
    client = ctx.request_context.lifespan_context.client

    classes_data = []

    for code in class_codes[:5]:  # Limit to 5 classes
        try:
            data = await client.get_class_details(
                class_code=code,
                language=language,
                include_features=True
            )
            classes_data.append(data)
        except Exception as e:
            logger.error(f"Error getting class {code}: {e}")
            classes_data.append({"code": code, "error": str(e)})

    return {
        "compared_classes": len(classes_data),
        "classes": classes_data,
        "language": language
    }


@mcp.tool()
async def search_values(
    search_text: str,
    language: str = "EN",
    deprecated: bool = False,
    max_results: int = 10,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Search ETIM feature values (colors, materials, connector types, etc.).

    Args:
        search_text: Search query
        language: Language code (EN, de-DE, nl-BE, etc.)
        deprecated: Include deprecated values
        max_results: Maximum number of results (1-100)

    Returns:
        Dictionary with matching values
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.search_values(
            search_text=search_text,
            language=language,
            deprecated=deprecated,
            from_=0,
            size=min(max_results, 100)
        )
        return result
    except Exception as e:
        logger.error(f"Error searching values: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_value_details(
    value_code: str,
    language: str = "EN",
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get detailed information about a specific ETIM value.

    Args:
        value_code: ETIM value code (e.g., "EV000397")
        language: Language code

    Returns:
        Value details including description and translations
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_value_details(
            value_code=value_code,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"Error getting value details: {e}")
        return {"error": str(e), "code": value_code}


@mcp.tool()
async def search_units(
    search_text: str,
    language: str = "EN",
    deprecated: bool = False,
    max_results: int = 10,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Search measurement units (millimeters, watts, volts, etc.).

    Args:
        search_text: Search query
        language: Language code
        deprecated: Include deprecated units
        max_results: Maximum number of results (1-100)

    Returns:
        Dictionary with matching units
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.search_units(
            search_text=search_text,
            language=language,
            deprecated=deprecated,
            from_=0,
            size=min(max_results, 100)
        )
        return result
    except Exception as e:
        logger.error(f"Error searching units: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_unit_details(
    unit_code: str,
    language: str = "EN",
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get detailed information about a specific measurement unit.

    Args:
        unit_code: ETIM unit code (e.g., "EU571097")
        language: Language code

    Returns:
        Unit details including description, abbreviation, and translations
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_unit_details(
            unit_code=unit_code,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"Error getting unit details: {e}")
        return {"error": str(e), "code": unit_code}


@mcp.tool()
async def search_feature_groups(
    search_text: str,
    language: str = "EN",
    max_results: int = 10,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Search ETIM feature groups (organizational categories for features).

    Args:
        search_text: Search query
        language: Language code
        max_results: Maximum number of results (1-100)

    Returns:
        Dictionary with matching feature groups
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.search_feature_groups(
            search_text=search_text,
            language=language,
            from_=0,
            size=min(max_results, 100)
        )
        return result
    except Exception as e:
        logger.error(f"Error searching feature groups: {e}")
        return {"error": str(e)}


@mcp.tool()
async def get_feature_group_details(
    feature_group_code: str,
    language: str = "EN",
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get detailed information about a specific feature group.

    Args:
        feature_group_code: ETIM feature group code (e.g., "EFG00004")
        language: Language code

    Returns:
        Feature group details including description and translations
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_feature_group_details(
            feature_group_code=feature_group_code,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"Error getting feature group details: {e}")
        return {"error": str(e), "code": feature_group_code}


@mcp.tool()
async def get_group_details(
    group_code: str,
    language: str = "EN",
    include_releases: bool = True,
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get detailed information about a specific product group.

    Args:
        group_code: ETIM group code (e.g., "EG020005")
        language: Language code
        include_releases: Include ETIM releases information

    Returns:
        Group details including description, translations, and releases
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_group_details(
            group_code=group_code,
            language=language,
            include_releases=include_releases
        )
        return result
    except Exception as e:
        logger.error(f"Error getting group details: {e}")
        return {"error": str(e), "code": group_code}


@mcp.tool()
async def get_class_diff(
    class_code: str,
    version: int,
    language: str = "EN",
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Get class details WITH changes compared to previous version.

    This tool shows what changed between class versions, making it perfect
    for understanding version migrations and tracking classification evolution.

    Args:
        class_code: ETIM class code (e.g., "EC000034")
        version: Class version to compare (must be version 2 or higher)
        language: Language code

    Returns:
        Class details with change information (added/removed/modified features)
    """
    client = ctx.request_context.lifespan_context.client

    try:
        result = await client.get_class_diff(
            class_code=class_code,
            version=version,
            language=language
        )
        return result
    except Exception as e:
        logger.error(f"Error getting class diff: {e}")
        return {"error": str(e), "code": class_code, "version": version}


@mcp.tool()
async def health_check(
    ctx: Context[ServerSession, AppContext] = None,
) -> dict:
    """
    Check server health and connection status.

    Returns:
        Health status of server components
    """
    client = ctx.request_context.lifespan_context.client
    cache = ctx.request_context.lifespan_context.cache

    redis_status = await cache.ping()
    api_status = await client.test_connection()

    return {
        "status": "healthy" if (redis_status and api_status) else "degraded",
        "redis": "connected" if redis_status else "disconnected",
        "etim_api": "connected" if api_status else "disconnected",
    }


# ============================================================================
# MCP RESOURCES
# ============================================================================

@mcp.resource("etim://languages")
async def get_languages_resource(
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Get list of supported languages as a resource"""
    client = ctx.request_context.lifespan_context.client

    try:
        languages = await client.get_allowed_languages()
        return f"Supported Languages:\n" + "\n".join(
            [f"- {lang['code']}: {lang['description']}" for lang in languages]
        )
    except Exception as e:
        return f"Error: {e}"


@mcp.resource("etim://releases")
async def get_releases_resource(
    ctx: Context[ServerSession, AppContext] = None,
) -> str:
    """Get ETIM releases as a resource"""
    client = ctx.request_context.lifespan_context.client

    try:
        releases = await client.get_releases()
        return f"ETIM Releases:\n" + "\n".join(
            [f"- {rel.get('code', 'N/A')}: {rel.get('description', 'N/A')}" for rel in releases]
        )
    except Exception as e:
        return f"Error: {e}"


# ============================================================================
# MCP PROMPTS
# ============================================================================

@mcp.prompt()
def compare_products_prompt(class1: str, class2: str, language: str = "EN") -> str:
    """Generate prompt for comparing two product classes"""
    return f"""Please compare these two ETIM product classes and highlight their differences:

Class 1: {class1}
Class 2: {class2}
Language: {language}

Use the compare_classes tool to get the data, then provide a clear comparison focusing on:
1. Product descriptions
2. Key feature differences
3. Use cases for each
4. Recommendations for which to choose based on requirements
"""


@mcp.prompt()
def find_product_by_specs_prompt(requirements: str, language: str = "EN") -> str:
    """Generate prompt to find products matching specifications"""
    return f"""I need to find ETIM product classes that match these requirements:

{requirements}

Language: {language}

Please:
1. Use search_classes to find relevant product categories
2. Get details on the most promising matches
3. Explain which products best fit the requirements and why
"""


@mcp.prompt()
def explain_classification_prompt(class_code: str, language: str = "EN") -> str:
    """Generate prompt explaining a classification"""
    return f"""Please explain the ETIM classification {class_code} in detail.

Language: {language}

Include:
1. What type of product this represents
2. Key technical features and characteristics
3. Typical use cases
4. Related product classifications

Use get_class_details with include_features=True to get the full information.
"""


# Entry point
if __name__ == "__main__":
    mcp.run()
