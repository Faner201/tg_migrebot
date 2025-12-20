"""Репозитории для работы с БД."""

from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.models import EntryModel, MedicationModel, SymptomModel, UserModel
from app.domain.models import Entry, Medication, Symptom, User
from app.domain.validators import EntryCreate, EntryUpdate, MedicationCreate, SymptomCreate


class UserRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Получить пользователя по Telegram ID."""
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return User.model_validate(model)

    async def create(self, telegram_id: int, username: str | None = None) -> User:
        """Создать нового пользователя."""
        model = UserModel(telegram_id=telegram_id, username=username)
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return User.model_validate(model)

    async def get_or_create(self, telegram_id: int, username: str | None = None) -> User:
        """Получить или создать пользователя."""
        user = await self.get_by_telegram_id(telegram_id)
        if user is None:
            user = await self.create(telegram_id, username)
            await self.session.commit()
        return user


class EntryRepository:
    """Репозиторий для работы с записями дневника."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: EntryCreate) -> Entry:
        """Создать новую запись."""
        model = EntryModel(
            user_id=data.user_id,
            entry_date=data.entry_date,
            pain_level=data.pain_level.value if data.pain_level else None,
            pain_score=data.pain_score,
            pain_description=data.pain_description,
            notes=data.notes,
            had_attack=data.had_attack,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return Entry.model_validate(model)

    async def get_by_id(self, entry_id: int) -> Entry | None:
        """Получить запись по ID."""
        stmt = select(EntryModel).where(EntryModel.id == entry_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Entry.model_validate(model)

    async def get_by_user_and_date(self, user_id: int, entry_date: date) -> Entry | None:
        """Получить запись пользователя за конкретную дату."""
        stmt = select(EntryModel).where(
            EntryModel.user_id == user_id, EntryModel.entry_date == entry_date
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return Entry.model_validate(model)

    async def update(self, entry_id: int, data: EntryUpdate) -> Entry | None:
        """Обновить запись."""
        stmt = select(EntryModel).where(EntryModel.id == entry_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None

        if data.pain_level is not None:
            model.pain_level = data.pain_level.value
        if data.pain_score is not None:
            model.pain_score = data.pain_score
        if data.pain_description is not None:
            model.pain_description = data.pain_description
        if data.notes is not None:
            model.notes = data.notes
        if data.had_attack is not None:
            model.had_attack = data.had_attack

        model.updated_at = datetime.utcnow()
        await self.session.flush()
        await self.session.refresh(model)
        return Entry.model_validate(model)

    async def list_by_user(
        self, user_id: int, limit: int = 30, offset: int = 0
    ) -> list[Entry]:
        """Получить список записей пользователя."""
        stmt = (
            select(EntryModel)
            .where(EntryModel.user_id == user_id)
            .order_by(EntryModel.entry_date.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [Entry.model_validate(m) for m in models]

    async def list_by_date_range(
        self, user_id: int, start_date: date, end_date: date
    ) -> list[Entry]:
        """Получить записи за период."""
        stmt = (
            select(EntryModel)
            .where(
                EntryModel.user_id == user_id,
                EntryModel.entry_date >= start_date,
                EntryModel.entry_date <= end_date,
            )
            .order_by(EntryModel.entry_date.desc())
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [Entry.model_validate(m) for m in models]


class MedicationRepository:
    """Репозиторий для работы с препаратами."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: MedicationCreate) -> Medication:
        """Создать запись о препарате."""
        model = MedicationModel(
            entry_id=data.entry_id,
            name=data.name,
            medication_type=data.medication_type,
            dosage=data.dosage,
            taken_at=data.taken_at,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return Medication.model_validate(model)

    async def list_by_entry(self, entry_id: int) -> list[Medication]:
        """Получить все препараты для записи."""
        stmt = select(MedicationModel).where(MedicationModel.entry_id == entry_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [Medication.model_validate(m) for m in models]


class SymptomRepository:
    """Репозиторий для работы с симптомами."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: SymptomCreate) -> Symptom:
        """Создать симптом."""
        model = SymptomModel(
            entry_id=data.entry_id,
            name=data.name,
            severity=data.severity,
        )
        self.session.add(model)
        await self.session.flush()
        await self.session.refresh(model)
        return Symptom.model_validate(model)

    async def list_by_entry(self, entry_id: int) -> list[Symptom]:
        """Получить все симптомы для записи."""
        stmt = select(SymptomModel).where(SymptomModel.entry_id == entry_id)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [Symptom.model_validate(m) for m in models]
