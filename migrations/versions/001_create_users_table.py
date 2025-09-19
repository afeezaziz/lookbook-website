"""Create users table

Revision ID: 001
Revises:
Create Date: 2024-01-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('profile_picture', sa.String(length=255), nullable=True),
        sa.Column('google_id', sa.String(length=50), nullable=True),
        sa.Column('access_token', sa.String(length=255), nullable=True),
        sa.Column('refresh_token', sa.String(length=255), nullable=True),
        sa.Column('token_expiry', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('google_id')
    )


def downgrade() -> None:
    op.drop_table('users')