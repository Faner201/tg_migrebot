"""Handlers для работы с записями дневника."""

import csv
import logging
from collections.abc import Iterable
from datetime import date, datetime, timedelta
from io import BytesIO, StringIO

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message
from openpyxl import Workbook

from app.adapters import get_session
from app.adapters.repository import EntryRepository, MedicationRepository, SymptomRepository
from app.domain.models import Entry, MedicationType, PainLevel, User
from app.domain.validators import EntryCreate, EntryUpdate, MedicationCreate

logger = logging.getLogger(__name__)
router = Router()

EXPORT_HEADERS = [
    "Дата",
    "Уровень боли (категория)",
    "Оценка боли (1-10)",
    "Описание боли",
    "Приступ",
    "Заметки",
]


def _entry_to_row(entry: Entry) -> list[str]:
    """Преобразовать запись в строку для экспорта."""
    return [
        entry.entry_date.isoformat(),
        entry.pain_level.value if entry.pain_level else "",
        str(entry.pain_score) if entry.pain_score is not None else "",
        entry.pain_description or "",
        "да" if entry.had_attack else "нет",
        entry.notes or "",
    ]


def build_csv(entries: Iterable[Entry]) -> bytes:
    """Сформировать CSV с записями."""
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(EXPORT_HEADERS)
    for entry in entries:
        writer.writerow(_entry_to_row(entry))
    return buffer.getvalue().encode("utf-8")


def build_xlsx(entries: Iterable[Entry]) -> bytes:
    """Сформировать XLSX с записями."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Записи"
    ws.append(EXPORT_HEADERS)
    for entry in entries:
        ws.append(_entry_to_row(entry))
    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()


@router.message(Command("headache"))
async def cmd_headache(message: Message, user: User) -> None:
    """Быстрый старт записи о головной боли."""
    today = date.today()
    async for session in get_session():
        repo = EntryRepository(session)
        existing = await repo.get_by_user_and_date(user.id, today)
        if existing:
            await message.answer(
                f"📝 У вас уже есть запись на сегодня.\n"
                f"Уровень боли: {existing.pain_level or 'не указан'}\n"
                f"Оценка боли (1-10): {existing.pain_score or 'не указана'}\n"
                f"Описание боли: {existing.pain_description or 'не указано'}\n"
                f"Приступ: {'да' if existing.had_attack else 'нет'}\n"
                f"Используйте /edit для редактирования."
            )
        else:
            await message.answer(
                "📝 Создайте запись о головной боли на сегодня.\n"
                "Используйте команды:\n"
                "/entry - создать запись\n"
                "/today - посмотреть сегодняшнюю запись"
            )
        break


@router.message(Command("entry"))
async def cmd_entry(message: Message, user: User) -> None:
    """Создать новую запись."""
    today = date.today()
    async for session in get_session():
        repo = EntryRepository(session)
        existing = await repo.get_by_user_and_date(user.id, today)
        if existing:
            await message.answer(
                "У вас уже есть запись на сегодня. Используйте /edit для редактирования."
            )
        else:
            # Создаем базовую запись
            entry_data = EntryCreate(
                user_id=user.id,
                entry_date=today,
                had_attack=False,
            )
            await repo.create(entry_data)
            await session.commit()
            await message.answer(
                f"✅ Запись создана на {today}.\n"
                "Установите оценку боли командой /set_score <1-10>.\n"
                "Добавьте описание боли через /set_pain_desc <текст> или заметки через /set_notes."
            )
        break


@router.message(Command("today"))
async def cmd_today(message: Message, user: User) -> None:
    """Показать сегодняшнюю запись."""
    today = date.today()
    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("📝 Записи на сегодня нет. Используйте /entry для создания.")
        else:
            med_repo = MedicationRepository(session)
            sym_repo = SymptomRepository(session)
            medications = await med_repo.list_by_entry(entry.id)
            symptoms = await sym_repo.list_by_entry(entry.id)

            text = f"📅 Запись на {entry.entry_date}:\n\n"
            text += f"Уровень боли: {entry.pain_level or 'не указан'}\n"
            text += f"Оценка боли (1-10): {entry.pain_score or 'не указана'}\n"
            if entry.pain_description:
                text += f"Описание боли: {entry.pain_description}\n"
            text += f"Приступ: {'да' if entry.had_attack else 'нет'}\n"
            if entry.notes:
                text += f"Заметки: {entry.notes}\n"
            if medications:
                text += f"\nПрепараты ({len(medications)}):\n"
                for med in medications:
                    text += f"  • {med.name}"
                    if med.dosage:
                        text += f" ({med.dosage})"
                    text += "\n"
            if symptoms:
                text += f"\nСимптомы ({len(symptoms)}):\n"
                for sym in symptoms:
                    text += f"  • {sym.name}"
                    if sym.severity:
                        text += f" (тяжесть: {sym.severity}/10)"
                    text += "\n"

            await message.answer(text)
        break


@router.message(Command("edit"))
async def cmd_edit(message: Message, user: User) -> None:
    """Редактировать сегодняшнюю запись."""
    today = date.today()
    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer(
                "Записи на сегодня нет. Сначала создайте её командой /entry."
            )
        else:
            await message.answer(
                "Редактирование записи.\n"
                "Используйте команды:\n"
                "/set_score <1-10> - установить оценку боли\n"
                "/set_pain_desc <текст> - добавить описание боли\n"
                "/set_pain <уровень> - установить уровень боли "
                "(none, mild, moderate, severe, very_severe)\n"
                "/set_notes <текст> - добавить заметки\n"
                "/set_attack - отметить приступ"
            )
        break


@router.message(Command("set_pain"))
async def cmd_set_pain(message: Message, user: User) -> None:
    """Установить уровень боли."""
    today = date.today()
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer(
            "Укажите уровень боли: none, mild, moderate, severe, very_severe"
        )
        return

    level_str = args[0].lower()
    try:
        pain_level = PainLevel(level_str)
    except ValueError:
        await message.answer(
            "Неверный уровень боли. Используйте: none, mild, moderate, "
            "severe, very_severe"
        )
        return

    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("Сначала создайте запись командой /entry.")
        else:
            update_data = EntryUpdate(pain_level=pain_level)
            await repo.update(entry.id, update_data)
            await session.commit()
            await message.answer(f"✅ Уровень боли установлен: {pain_level.value}")
        break


@router.message(Command("set_score"))
async def cmd_set_score(message: Message, user: User) -> None:
    """Установить оценку боли 1-10."""
    today = date.today()
    args = message.text.split()[1:] if message.text else []
    if not args:
        await message.answer("Укажите оценку боли от 1 до 10: /set_score 7")
        return

    try:
        score = int(args[0])
    except ValueError:
        await message.answer("Оценка должна быть числом от 1 до 10.")
        return

    if not 1 <= score <= 10:
        await message.answer("Оценка должна быть в диапазоне 1-10.")
        return

    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("Сначала создайте запись командой /entry.")
        else:
            update_data = EntryUpdate(pain_score=score)
            await repo.update(entry.id, update_data)
            await session.commit()
            await message.answer(f"✅ Оценка боли установлена: {score}/10.")
        break


@router.message(Command("set_pain_desc"))
async def cmd_set_pain_description(message: Message, user: User) -> None:
    """Добавить описание боли."""
    today = date.today()
    args = message.text.split(maxsplit=1)[1:] if message.text else []
    if not args:
        await message.answer(
            "Укажите описание после команды. "
            "Пример: /set_pain_desc пульсирующая боль"
        )
        return

    description = args[0]

    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("Сначала создайте запись командой /entry.")
        else:
            update_data = EntryUpdate(pain_description=description)
            await repo.update(entry.id, update_data)
            await session.commit()
            await message.answer("✅ Описание боли обновлено.")
        break


@router.message(Command("set_notes"))
async def cmd_set_notes(message: Message, user: User) -> None:
    """Установить заметки."""
    today = date.today()
    args = message.text.split(maxsplit=1)[1:] if message.text else []
    if not args:
        await message.answer("Укажите текст заметки после команды.")
        return

    notes = args[0]

    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("Сначала создайте запись командой /entry.")
        else:
            update_data = EntryUpdate(notes=notes)
            await repo.update(entry.id, update_data)
            await session.commit()
            await message.answer("✅ Заметки обновлены.")
        break


@router.message(Command("set_attack"))
async def cmd_set_attack(message: Message, user: User) -> None:
    """Отметить приступ."""
    today = date.today()
    async for session in get_session():
        repo = EntryRepository(session)
        entry = await repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("Сначала создайте запись командой /entry.")
        else:
            update_data = EntryUpdate(had_attack=True)
            await repo.update(entry.id, update_data)
            await session.commit()
            await message.answer("✅ Приступ отмечен в записи.")
        break


@router.message(Command("add_med"))
async def cmd_add_med(message: Message, user: User) -> None:
    """Добавить препарат."""
    today = date.today()
    args = message.text.split(maxsplit=2)[1:] if message.text else []
    if len(args) < 2:
        await message.answer(
            "Используйте: /add_med <тип> <название> [дозировка]\n"
            "Типы: preventive, abortive, other"
        )
        return

    med_type_str = args[0].lower()
    med_name = args[1]
    dosage = args[2] if len(args) > 2 else None

    try:
        med_type = MedicationType(med_type_str)
    except ValueError:
        await message.answer("Неверный тип препарата. Используйте: preventive, abortive, other")
        return

    async for session in get_session():
        entry_repo = EntryRepository(session)
        entry = await entry_repo.get_by_user_and_date(user.id, today)
        if entry is None:
            await message.answer("Сначала создайте запись командой /entry.")
        else:
            med_repo = MedicationRepository(session)
            med_data = MedicationCreate(
                entry_id=entry.id,
                name=med_name,
                medication_type=med_type.value,
                dosage=dosage,
                taken_at=datetime.utcnow(),
            )
            await med_repo.create(med_data)
            await session.commit()
            await message.answer(f"✅ Препарат добавлен: {med_name}")
        break


@router.message(Command("recent"))
async def cmd_recent(message: Message, user: User) -> None:
    """Показать последние записи."""
    async for session in get_session():
        repo = EntryRepository(session)
        entries = await repo.list_by_user(user.id, limit=10)
        if not entries:
            await message.answer("У вас пока нет записей.")
        else:
            text = "📋 Последние записи:\n\n"
            for entry in entries:
                text += f"📅 {entry.entry_date}\n"
                text += f"  Боль: {entry.pain_level or 'не указана'}\n"
                text += f"  Оценка: {entry.pain_score or 'не указана'}/10\n"
                if entry.pain_description:
                    text += f"  Описание: {entry.pain_description}\n"
                text += f"  Приступ: {'да' if entry.had_attack else 'нет'}\n\n"
            await message.answer(text)
        break


@router.message(Command("export"))
async def cmd_export(message: Message, user: User) -> None:
    """Сформировать выгрузку записей в CSV или XLSX (30 дней)."""
    args = message.text.split()[1:] if message.text else []
    export_format = args[0].lower() if args else "csv"
    if export_format not in {"csv", "xlsx"}:
        await message.answer("Укажите формат: /export csv или /export xlsx")
        return

    today = date.today()
    start_date = today - timedelta(days=30)

    async for session in get_session():
        repo = EntryRepository(session)
        entries = await repo.list_by_date_range(user.id, start_date, today)
        if not entries:
            await message.answer("Записей за последние 30 дней нет.")
            break

        if export_format == "csv":
            payload = build_csv(entries)
        else:
            payload = build_xlsx(entries)

        filename = (
            f"migrebot_entries_{start_date.isoformat()}_"
            f"{today.isoformat()}.{export_format}"
        )
        file = BufferedInputFile(payload, filename=filename)
        await message.answer_document(
            document=file,
            caption=(
                f"Выгрузка {len(entries)} записей за {start_date} — {today}.\n"
                "Включены оценка и описание боли."
            ),
        )
        break
