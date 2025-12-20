"""Добавить оценку боли и описание."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_add_pain_score_description"
down_revision: Union[str, None] = "0001_init"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("entries", sa.Column("pain_score", sa.Integer(), nullable=True))
    op.add_column("entries", sa.Column("pain_description", sa.Text(), nullable=True))
    op.create_check_constraint(
        "ck_entries_pain_score_range",
        "entries",
        "pain_score >= 1 AND pain_score <= 10",
    )


def downgrade() -> None:
    op.drop_constraint("ck_entries_pain_score_range", "entries", type_="check")
    op.drop_column("entries", "pain_description")
    op.drop_column("entries", "pain_score")


