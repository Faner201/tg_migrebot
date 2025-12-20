"""Redis клиент для кэша и сессий."""

import json
from typing import Optional

import redis.asyncio as redis

from app.config import settings


class RedisClient:
    """Клиент для работы с Redis."""

    def __init__(self) -> None:
        self._client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Подключиться к Redis."""
        if self._client is None:
            self._client = redis.from_url(settings.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        """Отключиться от Redis."""
        if self._client is not None:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis:
        """Получить клиент Redis."""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client

    async def get(self, key: str) -> Optional[str]:
        """Получить значение по ключу."""
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> None:
        """Установить значение с опциональным TTL."""
        await self.client.set(key, value, ex=ex)

    async def delete(self, key: str) -> None:
        """Удалить ключ."""
        await self.client.delete(key)

    async def get_json(self, key: str) -> Optional[dict]:
        """Получить JSON значение."""
        value = await self.get(key)
        if value is None:
            return None
        return json.loads(value)

    async def set_json(self, key: str, value: dict, ex: Optional[int] = None) -> None:
        """Установить JSON значение."""
        await self.set(key, json.dumps(value), ex=ex)

    async def exists(self, key: str) -> bool:
        """Проверить существование ключа."""
        return bool(await self.client.exists(key))


# Глобальный экземпляр
redis_client = RedisClient()
