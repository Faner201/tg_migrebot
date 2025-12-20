"""Доменные модели для дневника головной боли."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class PainLevel(str, Enum):
    """Уровень боли."""

    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    VERY_SEVERE = "very_severe"


class MedicationType(str, Enum):
    """Тип препарата."""

    PREVENTIVE = "preventive"
    ABORTIVE = "abortive"
    OTHER = "other"


class Entry(BaseModel):
    """Запись в дневнике."""

    id: int | None = None
    user_id: int
    entry_date: date
    pain_level: PainLevel | None = None
    pain_score: int | None = Field(None, ge=1, le=10)
    pain_description: str | None = Field(None, max_length=2000)
    notes: str | None = None
    had_attack: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class Medication(BaseModel):
    """Препарат."""

    id: int | None = None
    entry_id: int
    name: str = Field(..., min_length=1, max_length=200)
    medication_type: MedicationType
    dosage: str | None = None
    taken_at: datetime | None = None

    class Config:
        from_attributes = True


class Symptom(BaseModel):
    """Симптом."""

    id: int | None = None
    entry_id: int
    name: str = Field(..., min_length=1, max_length=200)
    severity: int | None = Field(None, ge=1, le=10)

    class Config:
        from_attributes = True


class User(BaseModel):
    """Пользователь бота."""

    id: int | None = None
    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    notification_time: str | None = None  # HH:MM format
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
