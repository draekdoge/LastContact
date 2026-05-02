"""перенумерация timer_alert_level под шаг «за 1 ч»

Было: 1=2ч, 2=30м, 3=10м
Стало: 1=2ч, 2=1ч, 3=30м, 4=10м

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE users SET timer_alert_level = CASE
                WHEN timer_alert_level >= 3 THEN 4
                WHEN timer_alert_level = 2 THEN 3
                ELSE timer_alert_level
            END
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            UPDATE users SET timer_alert_level = CASE
                WHEN timer_alert_level >= 4 THEN 3
                WHEN timer_alert_level = 3 THEN 2
                ELSE timer_alert_level
            END
            """
        )
    )
