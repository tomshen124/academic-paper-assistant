"""添加task_type字段到token_usage表

Revision ID: add_task_type_to_token_usage
Revises: 4cb3fad9633c
Create Date: 2023-06-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_task_type_to_token_usage'
down_revision = '4cb3fad9633c'
branch_labels = None
depends_on = None


def upgrade():
    # 添加task_type字段到token_usage表
    op.add_column('token_usage', sa.Column('task_type', sa.String(50), nullable=False, server_default='default', index=True))

    # 为现有记录设置默认值
    op.execute("UPDATE token_usage SET task_type = 'default'")


def downgrade():
    # 删除task_type字段
    op.drop_column('token_usage', 'task_type')
