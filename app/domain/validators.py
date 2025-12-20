"""Валидаторы для доменных данных."""

from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

from app.domain.models import PainLevel


class EntryCreate(BaseModel):
    """DTO для создания записи."""

    user_id: int
    entry_date: date
    pain_level: PainLevel | None = None
    pain_score: int | None = Field(None, ge=1, le=10)
    pain_description: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)
    had_attack: bool = False

    @field_validator("entry_date")
    @classmethod
    def validate_date_not_future(cls, v: date) -> date:
        """Проверка, что дата не в будущем."""
        today = date.today()
        if v > today:
            raise ValueError("Дата записи не может быть в будущем")
        return v


class EntryUpdate(BaseModel):
    """DTO для обновления записи."""

    pain_level: PainLevel | None = None
    pain_score: int | None = Field(None, ge=1, le=10)
    pain_description: str | None = Field(None, max_length=2000)
    notes: str | None = Field(None, max_length=2000)
    had_attack: bool | None = None


class MedicationCreate(BaseModel):
    """DTO для создания записи о препарате."""

    entry_id: int
    name: str = Field(..., min_length=1, max_length=200)
    medication_type: str
    dosage: str | None = Field(None, max_length=100)
    taken_at: datetime | None = None


class SymptomCreate(BaseModel):
    """DTO для создания симптома."""

    entry_id: int
    name: str = Field(..., min_length=1, max_length=200)
    severity: int | None = Field(None, ge=1, le=10)
