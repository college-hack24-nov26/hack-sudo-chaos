"""Initial database foundation matching Phase 1A backend models.

Revision ID: 0001_initial_foundation
Revises: 
Create Date: 2026-11-03 19:28:00.000000
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = '0001_initial_foundation'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Data Sources
    op.create_table(
        'data_sources',
        sa.Column('source_id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('license_type', sa.String(length=100), nullable=False),
        sa.Column('license_url', sa.Text(), nullable=False),
        sa.Column('attribution_text', sa.Text(), nullable=False),
        sa.Column('permits_redistribution', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('source_id')
    )

    # 2. Products
    op.create_table(
        'products',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('barcode', sa.String(length=32), nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=False),
        sa.Column('brand_name', sa.String(length=255), nullable=True),
        sa.Column('package_size', sa.String(length=100), nullable=True),
        sa.Column('serving_size_value', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('serving_size_unit', sa.String(length=20), nullable=False, server_default='g'),
        sa.Column('food_form', sa.String(length=20), nullable=False),
        sa.Column('food_category', sa.String(length=100), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('source_id', sa.String(length=50), nullable=True),
        sa.Column('source_retrieval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('raw_source_payload', JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("food_form IN ('solid', 'liquid')", name='chk_product_food_form'),
        sa.ForeignKeyConstraint(['source_id'], ['data_sources.source_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_barcode', 'products', ['barcode'], unique=True)
    op.create_index('ix_products_is_verified', 'products', ['is_verified'])

    # 3. Nutrients
    op.create_table(
        'nutrients',
        sa.Column('nutrient_code', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('standard_unit', sa.String(length=20), nullable=False),
        sa.Column('is_fssai_mandatory', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('icmr_nin_rda_adult', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('nutrient_code')
    )

    # 4. Product Nutrients
    op.create_table(
        'product_nutrients',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', UUID(as_uuid=True), nullable=False),
        sa.Column('nutrient_code', sa.String(length=50), nullable=False),
        sa.Column('per_100g_value', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('per_serving_value', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('data_status', sa.String(length=30), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "data_status IN ('PRESENT', 'UNKNOWN', 'EXPLICITLY_ZERO', 'NOT_DECLARED')",
            name='chk_product_nutrient_status'
        ),
        sa.ForeignKeyConstraint(['nutrient_code'], ['nutrients.nutrient_code']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'nutrient_code', name='uq_product_nutrient')
    )
    op.create_index('idx_product_nutrients_lookup', 'product_nutrients', ['product_id', 'nutrient_code'])

    # 5. Ingredients
    op.create_table(
        'ingredients',
        sa.Column('ingredient_code', sa.String(length=100), nullable=False),
        sa.Column('canonical_name', sa.String(length=255), nullable=False),
        sa.Column('ins_number', sa.String(length=50), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('is_fssai_major_allergen', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('functional_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint(
            "category IN ('SWEETENER', 'PRESERVATIVE', 'EMULSIFIER', 'FLAVOUR_ENHANCER', 'REFINED_CARB', 'FAT_OIL', 'PROTEIN', 'FIBRE', 'COLOUR', 'FORTIFICATION', 'OTHER')",
            name='chk_ingredient_category'
        ),
        sa.PrimaryKeyConstraint('ingredient_code')
    )
    op.create_index('ix_ingredients_ins_number', 'ingredients', ['ins_number'])

    # 6. Product Ingredients
    op.create_table(
        'product_ingredients',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', UUID(as_uuid=True), nullable=False),
        sa.Column('ingredient_code', sa.String(length=100), nullable=False),
        sa.Column('sequence_order', sa.Integer(), nullable=False),
        sa.Column('declared_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('is_allergen_declared', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('declared_label_text', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['ingredient_code'], ['ingredients.ingredient_code']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'sequence_order', name='uq_product_ingredient')
    )
    op.create_index('idx_product_ingredients_pid', 'product_ingredients', ['product_id'])

    # 7. Regulatory Claim Rules
    op.create_table(
        'regulatory_claim_rules',
        sa.Column('claim_id', sa.String(length=100), nullable=False),
        sa.Column('claim_code', sa.String(length=50), nullable=False),
        sa.Column('food_form', sa.String(length=20), nullable=False),
        sa.Column('operator', sa.String(length=10), nullable=False),
        sa.Column('threshold_value', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('unit', sa.String(length=30), nullable=False),
        sa.Column('fssai_regulation_reference', sa.Text(), nullable=False),
        sa.Column('consumer_explanation', sa.Text(), nullable=False),
        sa.CheckConstraint("food_form IN ('solid', 'liquid')", name='chk_claim_food_form'),
        sa.CheckConstraint("operator IN ('LTE', 'GTE', 'EQ')", name='chk_claim_operator'),
        sa.PrimaryKeyConstraint('claim_id')
    )

    # 8. Ingredient Rules
    op.create_table(
        'ingredient_rules',
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('ingredient_code', sa.String(length=100), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('condition_expression', sa.String(length=255), nullable=True),
        sa.Column('regulatory_reference', sa.Text(), nullable=False),
        sa.Column('consumer_guidance', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_code'], ['ingredients.ingredient_code']),
        sa.PrimaryKeyConstraint('rule_id')
    )

    # 9. Nutrition Interpretation Rules (Initial Baseline)
    op.create_table(
        'nutrition_interpretation_rules',
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('nutrient_code', sa.String(length=50), nullable=False),
        sa.Column('food_form', sa.String(length=20), nullable=False),
        sa.Column('low_threshold_max', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('moderate_threshold_max', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('high_threshold_min', sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('concern_level', sa.String(length=20), nullable=False),
        sa.Column('regulatory_citation', sa.Text(), nullable=False),
        sa.CheckConstraint("food_form IN ('solid', 'liquid')", name='chk_nir_food_form'),
        sa.CheckConstraint("concern_level IN ('POSITIVE', 'NEUTRAL', 'CONCERN')", name='chk_nir_concern_level'),
        sa.ForeignKeyConstraint(['nutrient_code'], ['nutrients.nutrient_code']),
        sa.PrimaryKeyConstraint('rule_id')
    )

    # 10. AI Explanations
    op.create_table(
        'ai_explanations',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('prompt_sha256', sa.String(length=64), nullable=False),
        sa.Column('generated_explanation', sa.Text(), nullable=False),
        sa.Column('is_fallback', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_ai_explanations_pid', 'ai_explanations', ['product_id'])

    # 11. Scan History
    op.create_table(
        'scan_history',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', UUID(as_uuid=True), nullable=True),
        sa.Column('barcode', sa.String(length=32), nullable=False),
        sa.Column('client_ip_hash', sa.String(length=64), nullable=True),
        sa.Column('scanned_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scan_history_barcode', 'scan_history', ['barcode'])


def downgrade() -> None:
    op.drop_table('scan_history')
    op.drop_table('ai_explanations')
    op.drop_table('nutrition_interpretation_rules')
    op.drop_table('ingredient_rules')
    op.drop_table('regulatory_claim_rules')
    op.drop_table('product_ingredients')
    op.drop_table('ingredients')
    op.drop_table('product_nutrients')
    op.drop_table('nutrients')
    op.drop_table('products')
    op.drop_table('data_sources')

