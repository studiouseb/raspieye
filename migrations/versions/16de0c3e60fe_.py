"""empty message

Revision ID: 16de0c3e60fe
Revises: 
Create Date: 2017-10-29 02:57:39.053329

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '16de0c3e60fe'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=60), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('uploads',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=256), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('file_name')
    )
    op.create_table('employees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_email'), 'employees', ['email'], unique=True)
    op.create_index(op.f('ix_employees_first_name'), 'employees', ['first_name'], unique=False)
    op.create_index(op.f('ix_employees_last_name'), 'employees', ['last_name'], unique=False)
    op.create_index(op.f('ix_employees_username'), 'employees', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_employees_username'), table_name='employees')
    op.drop_index(op.f('ix_employees_last_name'), table_name='employees')
    op.drop_index(op.f('ix_employees_first_name'), table_name='employees')
    op.drop_index(op.f('ix_employees_email'), table_name='employees')
    op.drop_table('employees')
    op.drop_table('uploads')
    op.drop_table('roles')
    op.drop_table('departments')
    # ### end Alembic commands ###
