"""Адаптеры для внешних сервисов (БД, Redis, почта, погода)."""

from app.adapters.database import async_session_maker, engine, get_session
from app.adapters.models import EntryModel, MedicationModel, SymptomModel, UserModel
from app.adapters.redis_client import redis_client
from app.adapters.repository import (
    EntryRepository,
    MedicationRepository,
    SymptomRepository,
    UserRepository,
)

__all__ = [
    "engine",
    "async_session_maker",
    "get_session",
    "UserModel",
    "EntryModel",
    "MedicationModel",
    "SymptomModel",
    "UserRepository",
    "EntryRepository",
    "MedicationRepository",
    "SymptomRepository",
    "redis_client",
]
