"""SQLAlchemy модели для БД."""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.database import Base


class UserModel(Base):
    """Модель пользователя."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notification_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # HH:MM
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    entries: Mapped[list["EntryModel"]] = relationship("EntryModel", back_populates="user")


class EntryModel(Base):
    """Модель записи в дневнике."""

    __tablename__ = "entries"
    __table_args__ = (
        CheckConstraint(
            "pain_score >= 1 AND pain_score <= 10",
            name="ck_entries_pain_score_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    entry_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    pain_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    pain_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pain_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    had_attack: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="entries")
    medications: Mapped[list["MedicationModel"]] = relationship(
        "MedicationModel", back_populates="entry", cascade="all, delete-orphan"
    )
    symptoms: Mapped[list["SymptomModel"]] = relationship(
        "SymptomModel", back_populates="entry", cascade="all, delete-orphan"
    )


class MedicationModel(Base):
    """Модель препарата."""

    __tablename__ = "medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entries.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    medication_type: Mapped[str] = mapped_column(String(20), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    entry: Mapped["EntryModel"] = relationship("EntryModel", back_populates="medications")


class SymptomModel(Base):
    """Модель симптома."""

    __tablename__ = "symptoms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("entries.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    entry: Mapped["EntryModel"] = relationship("EntryModel", back_populates="symptoms")
