"""Начальная схема БД для дневника боли."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_init"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("notification_time", sa.String(length=5), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)

    op.create_table(
        "entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("pain_level", sa.String(length=20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("had_attack", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_entries_user_date", "entries", ["user_id", "entry_date"], unique=True)
    op.create_index("ix_entries_user_id", "entries", ["user_id"])
    op.create_index("ix_entries_entry_date", "entries", ["entry_date"])

    op.create_table(
        "medications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("medication_type", sa.String(length=20), nullable=False),
        sa.Column("dosage", sa.String(length=100), nullable=True),
        sa.Column("taken_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["entry_id"], ["entries.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_medications_entry_id", "medications", ["entry_id"])

    op.create_table(
        "symptoms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["entry_id"], ["entries.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_symptoms_entry_id", "symptoms", ["entry_id"])


def downgrade() -> None:
    op.drop_index("ix_symptoms_entry_id", table_name="symptoms")
    op.drop_table("symptoms")
    op.drop_index("ix_medications_entry_id", table_name="medications")
    op.drop_table("medications")
    op.drop_index("ix_entries_entry_date", table_name="entries")
    op.drop_index("ix_entries_user_id", table_name="entries")
    op.drop_index("ix_entries_user_date", table_name="entries")
    op.drop_table("entries")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")



