"""add user column to calorie entry table. replace backref with back_populates

Revision ID: 57eda0ce6ab2
Revises: 553db079bd70
Create Date: 2023-06-12 20:18:50.577833

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.orm import relationship

# revision identifiers, used by Alembic.
revision = "57eda0ce6ab2"
down_revision = "553db079bd70"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # op.create_table(
    #     "tmp_calorie_entries",
    #     sa.Column("id", sa.Integer(), nullable=False),
    #     sa.Column("user_id", sa.Integer(), nullable=False),
    #     sa.Column("date", sa.Date(), nullable=False),
    #     sa.Column("time", sa.Time(), nullable=False),
    #     sa.Column("text", sa.String(), nullable=False),
    #     sa.Column("number_of_calories", sa.Integer()),
    #     sa.Column("is_below_expected", sa.Boolean()),
    #     sa.Column("created_at", sa.DateTime(), default=datetime.utcnow),
    #     sa.Column("updated_at", sa.DateTime(), default=datetime.utcnow),
    #     relationship("User", back_populates="calorie_entries"),
    #     sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    #     sa.PrimaryKeyConstraint("id"),
    # )

    # op.execute("INSERT INTO tmp_calorie_entries SELECT * FROM calorie_entries")

    # op.drop_table("calorie_entries")

    # op.rename_table("tmp_calorie_entries", "calorie_entries")
    # ### commands auto generated by Alembic - please adjust! ###
    # op.alter_column('calorie_entries', 'user_id',
    #            existing_type=sa.INTEGER(),
    #            nullable=True)
    # op.create_index(op.f('ix_calorie_entries_id'), 'calorie_entries', ['id'], unique=False)
    # op.drop_constraint(None, 'calorie_entries', type_='foreignkey')
    # op.create_foreign_key(None, 'calorie_entries', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###
    pass


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_constraint(None, 'calorie_entries', type_='foreignkey')
    # op.create_foreign_key(None, 'calorie_entries', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # op.drop_index(op.f('ix_calorie_entries_id'), table_name='calorie_entries')
    # op.alter_column('calorie_entries', 'user_id',
    #            existing_type=sa.INTEGER(),
    #            nullable=False)
    # ### end Alembic commands ###
    pass
