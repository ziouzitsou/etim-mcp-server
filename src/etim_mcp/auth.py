"""OAuth2 token management for ETIM API"""

import time
from typing import Optional
import httpx
from loguru import logger

from .cache import RedisCache
from .config import settings


class EtimTokenManager:
    """Manages OAuth2 access tokens for ETIM API with Redis caching"""

    TOKEN_CACHE_KEY = "etim:auth:token"
    TOKEN_EXPIRY_BUFFER = 300  # 5 minutes buffer before actual expiry

    def __init__(self, cache: RedisCache):
        """
        Initialize token manager

        Args:
            cache: Redis cache instance
        """
        self.cache = cache
        self.client_id = settings.etim_client_id
        self.client_secret = settings.etim_client_secret
        self.auth_url = settings.etim_auth_url
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if not self._http_client:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def get_token(self) -> str:
        """
        Get valid access token (from cache or by fetching new one)

        Returns:
            Valid access token

        Raises:
            Exception: If unable to obtain token
        """
        # Try to get token from cache
        cached_data = await self.cache.get(self.TOKEN_CACHE_KEY)

        if cached_data:
            token = cached_data.get("access_token")
            expires_at = cached_data.get("expires_at", 0)

            # Check if token is still valid (with buffer)
            if time.time() < (expires_at - self.TOKEN_EXPIRY_BUFFER):
                logger.debug("Using cached access token")
                return token

            logger.info("Cached token expired, fetching new one")

        # Fetch new token
        return await self._fetch_new_token()

    async def _fetch_new_token(self) -> str:
        """
        Fetch new access token from ETIM auth server

        Returns:
            New access token

        Raises:
            Exception: If token fetch fails
        """
        logger.info("Fetching new access token from ETIM")

        client = await self._get_http_client()

        try:
            response = await client.post(
                f"{self.auth_url}/connect/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "scope": "EtimApi",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            response.raise_for_status()
            data = response.json()

            access_token = data["access_token"]
            expires_in = data["expires_in"]  # Usually 3600 seconds (1 hour)

            # Calculate expiry time
            expires_at = time.time() + expires_in

            # Cache the token (with buffer)
            cache_ttl = expires_in - self.TOKEN_EXPIRY_BUFFER
            await self.cache.set(
                self.TOKEN_CACHE_KEY,
                {"access_token": access_token, "expires_at": expires_at},
                ttl=cache_ttl,
            )

            logger.info(f"New access token obtained (expires in {expires_in}s)")
            return access_token

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching token: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to obtain access token: {e}")
        except Exception as e:
            logger.error(f"Error fetching token: {e}")
            raise

    async def refresh_token(self) -> str:
        """
        Force refresh of access token

        Returns:
            New access token
        """
        logger.info("Forcing token refresh")
        await self.cache.delete(self.TOKEN_CACHE_KEY)
        return await self._fetch_new_token()

    async def close(self):
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            logger.debug("Token manager HTTP client closed")
