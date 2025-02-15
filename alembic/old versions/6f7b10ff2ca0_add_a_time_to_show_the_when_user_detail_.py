"""add a time to show the when user detail is updated

Revision ID: 6f7b10ff2ca0
Revises: 8ab2c2fca3c2
Create Date: 2023-06-11 01:33:11.160823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6f7b10ff2ca0"
down_revision = "8ab2c2fca3c2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "updated_at")
    # ### end Alembic commands ###
