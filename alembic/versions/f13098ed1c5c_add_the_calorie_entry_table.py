"""add the calorie entry table

Revision ID: f13098ed1c5c
Revises: bd7e8854faaf
Create Date: 2023-06-10 22:46:25.989233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f13098ed1c5c"
down_revision = "bd7e8854faaf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "calorie_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time", sa.Time(), nullable=False),
        sa.Column("text", sa.String(), nullable=False),
        sa.Column("number_of_calories", sa.Integer(), nullable=True),
        sa.Column("is_below_expected", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_calorie_entries_id"), "calorie_entries", ["id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_calorie_entries_id"), table_name="calorie_entries")
    op.drop_table("calorie_entries")
    # ### end Alembic commands ###
