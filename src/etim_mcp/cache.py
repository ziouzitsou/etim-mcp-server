"""Redis cache wrapper for ETIM API responses"""

import json
from typing import Any, Optional
import redis.asyncio as redis
from loguru import logger


class RedisCache:
    """Async Redis cache for API responses"""

    def __init__(self, host: str, port: int, password: str = ""):
        """
        Initialize Redis client

        Args:
            host: Redis server hostname
            port: Redis server port
            password: Redis password (optional)
        """
        self.host = host
        self.port = port
        self.password = password
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Establish Redis connection"""
        try:
            self.client = await redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password if self.password else None,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
            )
            await self.client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """
        Get cached value by key

        Args:
            key: Cache key

        Returns:
            Cached value (deserialized from JSON) or None if not found
        """
        if not self.client:
            logger.warning("Redis client not connected")
            return None

        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Set cache value with TTL

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            logger.warning("Redis client not connected")
            return False

        try:
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete cached value

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        if not self.client:
            return False

        try:
            result = await self.client.delete(key)
            logger.debug(f"Deleted cache key: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False

    async def ping(self) -> bool:
        """
        Check if Redis is responsive

        Returns:
            True if Redis responds to ping, False otherwise
        """
        if not self.client:
            return False

        try:
            await self.client.ping()
            return True
        except Exception:
            return False

    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")

    def generate_key(self, prefix: str, *args: Any) -> str:
        """
        Generate a cache key from prefix and arguments

        Args:
            prefix: Key prefix (e.g., 'class', 'feature')
            *args: Key components

        Returns:
            Generated cache key
        """
        parts = [prefix] + [str(arg) for arg in args if arg is not None]
        return ":".join(parts)
