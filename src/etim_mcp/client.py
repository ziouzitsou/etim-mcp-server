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
        modelling: Optional[bool] = None,
        filters: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Search ETIM product classes

        Args:
            search_text: Search query
            language: Language code (defaults to configured default)
            from_: Pagination offset
            size: Number of results
            modelling: Include only modelling classes (True) or exclude them (False), None for both
            filters: List of filter dictionaries with 'code' and 'values' keys
                     Example: [{"code": "Release", "values": ["ETIM-9.0"]},
                              {"code": "Group", "values": ["EG000017", "EG000020"]}]
                     Supported filter codes: Release, Group, Class, Feature, Value

        Returns:
            Search results with total and list of classes
        """
        language = language or self.default_language

        # Build cache key including filters
        filter_key = None
        if filters:
            filter_key = tuple(
                f"{f['code']}:{','.join(sorted(f['values']))}"
                for f in sorted(filters, key=lambda x: x['code'])
            )

        cache_key = self.cache.generate_key(
            "search:class", search_text, language, modelling, filter_key, from_, size
        )
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        # Make API request
        filter_desc = f" with {len(filters)} filters" if filters else ""
        modelling_desc = f" (modelling={modelling})" if modelling is not None else ""
        logger.info(f"Searching classes: '{search_text}' (lang: {language}){filter_desc}{modelling_desc}")

        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
        }

        # Add modelling flag if specified
        if modelling is not None:
            data["modelling"] = modelling

        # Add filters if specified
        if filters:
            data["filters"] = filters

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

        # Always include descriptions and translations for synonyms
        data["include"] = {
            "descriptions": True,
            "translations": True,
        }

        # Optionally include features
        if include_features:
            data["include"]["fields"] = ["Features", "Group"]
        else:
            data["include"]["fields"] = ["Group"]

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

    async def get_all_languages(self) -> List[Dict[str, str]]:
        """
        Get list of ALL ETIM languages (not just account-specific)

        Returns:
            List of all language dictionaries with code and description
        """
        cache_key = "languages:all"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info("Getting all ETIM languages")
        result = await self._make_request("GET", "/api/v2/Misc/Languages")

        # Cache with long TTL
        await self.cache.set(cache_key, result, settings.cache_languages_ttl)

        return result

    async def get_class_details_many(
        self,
        classes: List[Dict[str, Any]],
        language: str = None,
        include_features: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get details for multiple classes in a single request (batch operation)

        Args:
            classes: List of class objects with 'code' and optionally 'version'
                    e.g., [{"code": "EC001744", "version": 5}, {"code": "EC002710"}]
            language: Language code
            include_features: Whether to include features

        Returns:
            List of class details
        """
        language = language or self.default_language

        # Generate cache key from class codes/versions
        class_keys = tuple(f"{c['code']}:{c.get('version', 'latest')}" for c in classes)
        cache_key = self.cache.generate_key("class:many", class_keys, language, include_features)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting details for {len(classes)} classes (lang: {language})")
        data = {
            "classes": classes,
            "languagecode": language,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        if include_features:
            data["include"]["fields"] = ["Features", "Group", "Releases"]
        else:
            data["include"]["fields"] = ["Group", "Releases"]

        result = await self._make_request("POST", "/api/v2/Class/DetailsMany", data)

        # Cache with longer TTL
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def get_all_class_versions(
        self,
        class_code: str,
        language: str = None,
        include_features: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get ALL versions of a specific class

        Args:
            class_code: ETIM class code (e.g., EC002883)
            language: Language code
            include_features: Whether to include features for each version

        Returns:
            List of all class versions with details
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("class:allversions", class_code, language, include_features)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting all versions of class: {class_code} (lang: {language})")
        data = {
            "code": class_code,
            "languagecode": language,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        if include_features:
            data["include"]["fields"] = ["Features", "Group", "Releases"]
        else:
            data["include"]["fields"] = ["Group", "Releases"]

        result = await self._make_request("POST", "/api/v2/Class/DetailsManyByCode", data)

        # Cache with longer TTL
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def get_class_for_release(
        self,
        class_code: str,
        release: str,
        language: str = None,
        include_features: bool = True,
    ) -> Dict[str, Any]:
        """
        Get class details for a specific ETIM release

        Args:
            class_code: ETIM class code (e.g., EC000034)
            release: ETIM release name (e.g., "ETIM-9.0", "DYNAMIC")
            language: Language code
            include_features: Whether to include features

        Returns:
            Class details for the specified release
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("class:release", class_code, release, language, include_features)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting class {class_code} for release {release} (lang: {language})")
        data = {
            "code": class_code,
            "release": release,
            "languagecode": language,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        if include_features:
            data["include"]["fields"] = ["Features", "Group", "Releases"]
        else:
            data["include"]["fields"] = ["Group", "Releases"]

        result = await self._make_request("POST", "/api/v2/Class/DetailsForRelease", data)

        # Cache with longer TTL
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def search_values(
        self,
        search_text: str,
        language: str = None,
        deprecated: bool = False,
        from_: int = 0,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search ETIM feature values

        Args:
            search_text: Search query
            language: Language code
            deprecated: Include deprecated values
            from_: Pagination offset
            size: Number of results

        Returns:
            Search results
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("search:value", search_text, language, deprecated, from_, size)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Searching values: '{search_text}' (lang: {language})")
        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
            "deprecated": deprecated,
            "include": {"descriptions": True},
        }

        result = await self._make_request("POST", "/api/v2/Value/Search", data)
        await self.cache.set(cache_key, result, settings.cache_ttl)

        return result

    async def get_value_details(
        self,
        value_code: str,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Get value details

        Args:
            value_code: ETIM value code (e.g., EV000397)
            language: Language code

        Returns:
            Value details
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("value", value_code, language)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting value details: {value_code} (lang: {language})")
        data = {
            "languagecode": language,
            "code": value_code,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        result = await self._make_request("POST", "/api/v2/Value/Details", data)
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def search_units(
        self,
        search_text: str,
        language: str = None,
        deprecated: bool = False,
        from_: int = 0,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search measurement units

        Args:
            search_text: Search query
            language: Language code
            deprecated: Include deprecated units
            from_: Pagination offset
            size: Number of results

        Returns:
            Search results
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("search:unit", search_text, language, deprecated, from_, size)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Searching units: '{search_text}' (lang: {language})")
        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
            "deprecated": deprecated,
            "include": {"descriptions": True},
        }

        result = await self._make_request("POST", "/api/v2/Unit/Search", data)
        await self.cache.set(cache_key, result, settings.cache_ttl)

        return result

    async def get_unit_details(
        self,
        unit_code: str,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Get unit details

        Args:
            unit_code: ETIM unit code (e.g., EU571097)
            language: Language code

        Returns:
            Unit details
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("unit", unit_code, language)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting unit details: {unit_code} (lang: {language})")
        data = {
            "languagecode": language,
            "code": unit_code,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        result = await self._make_request("POST", "/api/v2/Unit/Details", data)
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def search_feature_groups(
        self,
        search_text: str,
        language: str = None,
        from_: int = 0,
        size: int = 10,
    ) -> Dict[str, Any]:
        """
        Search feature groups

        Args:
            search_text: Search query
            language: Language code
            from_: Pagination offset
            size: Number of results

        Returns:
            Search results
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("search:featuregroup", search_text, language, from_, size)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Searching feature groups: '{search_text}' (lang: {language})")
        data = {
            "languagecode": language,
            "from": from_,
            "size": size,
            "searchString": search_text,
            "include": {"descriptions": True},
        }

        result = await self._make_request("POST", "/api/v2/FeatureGroup/Search", data)
        await self.cache.set(cache_key, result, settings.cache_ttl)

        return result

    async def get_feature_group_details(
        self,
        feature_group_code: str,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Get feature group details

        Args:
            feature_group_code: ETIM feature group code (e.g., EFG00004)
            language: Language code

        Returns:
            Feature group details
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("featuregroup", feature_group_code, language)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting feature group details: {feature_group_code} (lang: {language})")
        data = {
            "languagecode": language,
            "code": feature_group_code,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        result = await self._make_request("POST", "/api/v2/FeatureGroup/Details", data)
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def get_group_details(
        self,
        group_code: str,
        language: str = None,
        include_releases: bool = True,
    ) -> Dict[str, Any]:
        """
        Get product group details

        Args:
            group_code: ETIM group code (e.g., EG020005)
            language: Language code
            include_releases: Include releases information

        Returns:
            Group details
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("group", group_code, language, include_releases)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting group details: {group_code} (lang: {language})")
        data = {
            "languagecode": language,
            "code": group_code,
            "include": {
                "descriptions": True,
                "translations": True,
            },
        }

        if include_releases:
            data["include"]["fields"] = ["Releases"]

        result = await self._make_request("POST", "/api/v2/Group/Details", data)
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

        return result

    async def get_class_diff(
        self,
        class_code: str,
        version: int,
        language: str = None,
    ) -> Dict[str, Any]:
        """
        Get class details with differences compared to previous version

        Args:
            class_code: ETIM class code (e.g., EC000034)
            version: Class version to compare
            language: Language code

        Returns:
            Class details with change information
        """
        language = language or self.default_language

        cache_key = self.cache.generate_key("class:diff", class_code, version, language)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        logger.info(f"Getting class diff: {class_code} v{version} (lang: {language})")
        data = {
            "languagecode": language,
            "code": class_code,
            "version": version,
            "include": {
                "descriptions": True,
                "translations": True,
                "fields": ["Group", "Releases", "Features"],
            },
        }

        result = await self._make_request("POST", "/api/v2/Class/DetailsDiff", data)
        await self.cache.set(cache_key, result, settings.cache_class_ttl)

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
