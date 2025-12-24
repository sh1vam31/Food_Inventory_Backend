"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create raw_materials table
    op.create_table('raw_materials',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('unit', sa.String(), nullable=False),
    sa.Column('quantity_available', sa.Float(), nullable=False),
    sa.Column('minimum_threshold', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_raw_materials_id'), 'raw_materials', ['id'], unique=False)
    op.create_index(op.f('ix_raw_materials_name'), 'raw_materials', ['name'], unique=True)

    # Create food_items table
    op.create_table('food_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_items_id'), 'food_items', ['id'], unique=False)
    op.create_index(op.f('ix_food_items_name'), 'food_items', ['name'], unique=False)

    # Create orders table
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('PLACED', 'CANCELLED', 'COMPLETED', name='orderstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)

    # Create food_item_ingredients table
    op.create_table('food_item_ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('food_item_id', sa.Integer(), nullable=False),
    sa.Column('raw_material_id', sa.Integer(), nullable=False),
    sa.Column('quantity_required_per_unit', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['food_item_id'], ['food_items.id'], ),
    sa.ForeignKeyConstraint(['raw_material_id'], ['raw_materials.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_food_item_ingredients_id'), 'food_item_ingredients', ['id'], unique=False)

    # Create order_items table
    op.create_table('order_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('food_item_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Float(), nullable=False),
    sa.Column('subtotal', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['food_item_id'], ['food_items.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_food_item_ingredients_id'), table_name='food_item_ingredients')
    op.drop_table('food_item_ingredients')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')
    op.drop_index(op.f('ix_food_items_name'), table_name='food_items')
    op.drop_index(op.f('ix_food_items_id'), table_name='food_items')
    op.drop_table('food_items')
    op.drop_index(op.f('ix_raw_materials_name'), table_name='raw_materials')
    op.drop_index(op.f('ix_raw_materials_id'), table_name='raw_materials')
    op.drop_table('raw_materials')