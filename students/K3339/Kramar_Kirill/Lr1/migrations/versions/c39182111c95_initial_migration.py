"""Initial migration

Revision ID: c39182111c95
Revises:
Create Date: 2025-04-13 20:12:15.977173

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c39182111c95"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


task_priority_enum = sa.Enum(
    "low",
    "medium",
    "high",
    "critical",
    name="taskpriority",
)

task_status_enum = sa.Enum(
    "todo",
    "in_progress",
    "done",
    "cancelled",
    name="taskstatus",
)


def upgrade() -> None:
    task_priority_enum.create(op.get_bind(), checkfirst=True)
    task_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_user_username", "user", ["username"], unique=True)
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "taskcategory",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("color_code", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
    )
    op.create_index("ix_taskcategory_name", "taskcategory", ["name"], unique=False)

    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
    )
    op.create_index("ix_tag_name", "tag", ["name"], unique=False)

    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("priority", task_priority_enum, nullable=False),
        sa.Column("status", task_status_enum, nullable=False),
        sa.Column("estimated_time_minutes", sa.Integer(), nullable=False),
        sa.Column("actual_time_minutes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column(
            "category_id",
            sa.Integer(),
            sa.ForeignKey("taskcategory.id"),
            nullable=True,
        ),
    )
    op.create_index("ix_task_title", "task", ["title"], unique=False)

    op.create_table(
        "tasktag",
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id"), nullable=False),
        sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tag.id"), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("task_id", "tag_id"),
    )

    op.create_table(
        "reminder",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("remind_at", sa.DateTime(), nullable=False),
        sa.Column("is_sent", sa.Boolean(), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("task.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("reminder")
    op.drop_table("tasktag")

    op.drop_index("ix_task_title", table_name="task")
    op.drop_table("task")

    op.drop_index("ix_tag_name", table_name="tag")
    op.drop_table("tag")

    op.drop_index("ix_taskcategory_name", table_name="taskcategory")
    op.drop_table("taskcategory")

    op.drop_index("ix_user_email", table_name="user")
    op.drop_index("ix_user_username", table_name="user")
    op.drop_table("user")

    task_status_enum.drop(op.get_bind(), checkfirst=True)
    task_priority_enum.drop(op.get_bind(), checkfirst=True)
