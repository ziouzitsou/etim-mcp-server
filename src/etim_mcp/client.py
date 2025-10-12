"""ETIM API client with caching and error handling"""

from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

from .auth import EtimTokenManager
from .cache import RedisCache
from .config import settings


class EtimAPIClient:
    """Async client for ETIM API with Redis caching"""

    def __init__(self, token_manager: EtimTokenManager, cache: RedisCache):
        """
        Initialize ETIM API client

        Args:
            token_manager: OAuth token manager
            cache: Redis cache instance
        """
        self.token_manager = token_manager
        self.cache = cache
        self.api_url = settings.etim_api_url
        self.default_language = settings.etim_default_language
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if not self._http_client:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        retry_on_401: bool = True,
    ) -> Dict[str, Any]:
        """
        Make authenticated API request

        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint path
            data: Request body for POST requests
            retry_on_401: Whether to retry once on 401 error

        Returns:
            Response data

        Raises:
            Exception: If request fails
        """
        token = await self.token_manager.get_token()
        client = await self._get_http_client()
        url = f"{self.api_url}{endpoint}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        if method == "POST":
            headers["Content-Type"] = "application/json"

        try:
            if method == "GET":
                response = await client.get(url, headers=headers)
            else:  # POST
                response = await client.post(url, headers=headers, json=data)

            # Handle 401 with token refresh
            if response.status_code == 401 and retry_on_401:
                logger.warning("Received 401, refreshing token and retrying")
                await self.token_manager.refresh_token()
                return await self._make_request(method, endpoint, data, retry_on_401=False)

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise

    async def search_classes(
        self,
        search_text: str,
        language: str = None,
        from_: int = 0,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search ETIM product classes

        Args:
            search_text: Search query
            language: Language code (defaults to configured default)
            from_: Pagination offset
            size: Number of results

        Returns:
            Search results with total and list of classes
        """
        language = language or self.default_language

        # Check cache
        cache_key = self.cache.generate_key("search:class", search_text, language, from_, size)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Make API request
        logger.info(f"Searching classes: '{search_text}' (lang: {language})")
        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
        }

        result = await self._make_request("POST", "/api/v2/Class/Search", data)

        # Cache result
        await self.cache.set(cache_key, result, settings.cache_ttl)

        return result

    async def get_class_details(
        self,
        class_code: str,
        version: Optional[int] = None,
        language: str = None,
        include_features: bool = True,
    ) -> Dict[str, Any]:
        """
        Get detailed information about a product class

        Args:
            class_code: ETIM class code (e.g., EC001744)
            version: Class version (latest if not specified)
            language: Language code
            include_features: Whether to include features

        Returns:
            Class details
        """
        language = language or self.default_language

        # Check cache
        cache_key = self.cache.generate_key("class", class_code, version, language, include_features)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Make API request
        logger.info(f"Getting class details: {class_code} v{version} (lang: {language})")
        data = {
            "languagecode": language,
            "code": class_code,
        }

        if version is not None:
            data["version"] = version

        if include_features:
            data["include"] = {
                "descriptions": True,
                "fields": ["Features", "Group"],
            }

        result = await self._make_request("POST", "/api/v2/Class/Details", data)

        # Cache with longer TTL
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def search_features(
        self,
        search_text: str,
        language: str = None,
        from_: int = 0,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search ETIM features

        Args:
            search_text: Search query
            language: Language code
            from_: Pagination offset
            size: Number of results

        Returns:
            Search results
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("search:feature", search_text, language, from_, size)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Searching features: '{search_text}' (lang: {language})")
        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
        }

        result = await self._make_request("POST", "/api/v2/Feature/Search", data)
        await self.cache.set(cache_key, result, settings.cache_ttl)

        return result

    async def get_feature_details(
        self,
        feature_code: str,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Get feature details

        Args:
            feature_code: ETIM feature code (e.g., EF007793)
            language: Language code

        Returns:
            Feature details
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("feature", feature_code, language)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting feature details: {feature_code} (lang: {language})")
        data = {
            "languagecode": language,
            "code": feature_code,
            "include": {"descriptions": True},
        }

        result = await self._make_request("POST", "/api/v2/Feature/Details", data)
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def search_groups(
        self,
        search_text: str,
        language: str = None,
        from_: int = 0,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search product groups

        Args:
            search_text: Search query
            language: Language code
            from_: Pagination offset
            size: Number of results

        Returns:
            Search results
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("search:group", search_text, language, from_, size)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Searching groups: '{search_text}' (lang: {language})")
        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
        }

        result = await self._make_request("POST", "/api/v2/Group/Search", data)
        await self.cache.set(cache_key, result, settings.cache_ttl)

        return result

    async def get_allowed_languages(self) -> List[Dict[str, str]]:
        """
        Get list of allowed languages for this account

        Returns:
            List of language dictionaries with code and description
        """
        cache_key = "languages:allowed"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info("Getting allowed languages")
        result = await self._make_request("GET", "/api/v2/Misc/LanguagesAllowed")

        # Cache with long TTL
        await self.cache.set(cache_key, result, settings.cache_languages_ttl)

        return result

    async def get_releases(self) -> List[Dict[str, Any]]:
        """
        Get list of ETIM releases

        Returns:
            List of release information
        """
        cache_key = "releases"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info("Getting ETIM releases")
        result = await self._make_request("GET", "/api/v2/Misc/Releases")

        # Cache with long TTL
        await self.cache.set(cache_key, result, settings.cache_languages_ttl)

        return result

    async def test_connection(self) -> bool:
        """
        Test API connection

        Returns:
            True if connection works, False otherwise
        """
        try:
            await self.get_allowed_languages()
            return True
        except Exception:
            return False

    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            logger.debug("ETIM API client closed")
