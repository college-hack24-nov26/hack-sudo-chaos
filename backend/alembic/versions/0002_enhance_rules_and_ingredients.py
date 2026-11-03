"""Enhance nutrition and regulatory rules schema per Phase 1B approved contract and audit remediation.

Revision ID: 0002_enhance_rules_and_ingredients
Revises: 0001_initial_foundation
Create Date: 2026-11-03 20:30:00.000000

Remediations Implemented:
1. DEF-01: Separated ICMR Table 15.1 (icmr_nutrient_threshold_rules) and Table 15.2 (icmr_matrix_rules).
2. DEF-02: condition_expression is nullable without invalid '{}' server default.
3. DEF-03: processing_classification and sugar_classification include 'UNKNOWN' and 'INSUFFICIENT_EVIDENCE', defaulting to 'UNKNOWN'.
4. DEF-06: Reconciled ingredient_rules check constraint to support both foundational and enhanced rule types.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = '0002_enhance_rules'
down_revision: Union[str, None] = '0001_initial_foundation'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Enhance nutrients table
    # -------------------------------------------------------------------------
    op.add_column(
        'nutrients',
        sa.Column('fssai_standard_daily_rdi', sa.Numeric(precision=10, scale=2), nullable=True)
    )
    op.add_column(
        'nutrients',
        sa.Column(
            'rdi_citation',
            sa.Text(),
            nullable=True,
            server_default='FSSAI Labelling and Display Regulations 2020, Reg 5(3)(b)'
        )
    )

    # -------------------------------------------------------------------------
    # 2. Enhance ingredients table (DEF-03: default UNKNOWN, includes INSUFFICIENT_EVIDENCE)
    # -------------------------------------------------------------------------
    op.add_column(
        'ingredients',
        sa.Column(
            'processing_classification',
            sa.String(length=30),
            nullable=False,
            server_default='UNKNOWN'
        )
    )
    op.add_column(
        'ingredients',
        sa.Column(
            'sugar_classification',
            sa.String(length=30),
            nullable=False,
            server_default='UNKNOWN'
        )
    )
    op.add_column(
        'ingredients',
        sa.Column('classification_evidence', sa.Text(), nullable=True)
    )
    op.create_check_constraint(
        'chk_ingredient_proc_class',
        'ingredients',
        "processing_classification IN ('WHOLE_FOOD', 'CULINARY_PROCESSED', 'FUNCTIONAL_ADDITIVE', 'COSMETIC_ADDITIVE', 'INDUSTRIAL_FRACTION', 'INSUFFICIENT_EVIDENCE', 'UNKNOWN')"
    )
    op.create_check_constraint(
        'chk_ingredient_sugar_class',
        'ingredients',
        "sugar_classification IN ('NOT_SUGAR', 'INTRINSIC_SUGAR', 'ADDED_FREE_SUGAR', 'SUGAR_SUBSTITUTE_SWEETENER', 'NON_NUTRITIVE_SWEETENER', 'POLYOL', 'INSUFFICIENT_EVIDENCE', 'UNKNOWN')"
    )

    # -------------------------------------------------------------------------
    # 3. Enhance regulatory_claim_rules table (DEF-02: nullable condition_expression)
    # -------------------------------------------------------------------------
    op.drop_constraint('chk_claim_operator', 'regulatory_claim_rules', type_='check')
    op.drop_constraint('chk_claim_food_form', 'regulatory_claim_rules', type_='check')

    op.add_column(
        'regulatory_claim_rules',
        sa.Column('claim_title', sa.String(length=150), nullable=False, server_default='')
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column(
            'claim_family',
            sa.String(length=50),
            nullable=False,
            server_default='NUTRIENT_CONTENT_CLAIM'
        )
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column('applicable_category', sa.String(length=100), nullable=False, server_default='ALL')
    )
    # DEF-02 Fix: Nullable condition_expression without invalid '{}' server default
    op.add_column(
        'regulatory_claim_rules',
        sa.Column('condition_expression', JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column('permitted_synonyms_schedule_ii', JSONB(astext_type=sa.Text()), nullable=False, server_default='[]')
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column(
            'official_source_version',
            sa.String(length=50),
            nullable=False,
            server_default='Version III (04-10-2022)'
        )
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column('effective_from', sa.Date(), nullable=False, server_default='2019-07-01')
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column('effective_to', sa.Date(), nullable=True)
    )
    op.add_column(
        'regulatory_claim_rules',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true'))
    )

    op.alter_column('regulatory_claim_rules', 'operator', existing_type=sa.String(length=10), nullable=True)
    op.alter_column('regulatory_claim_rules', 'threshold_value', existing_type=sa.Numeric(precision=10, scale=3), nullable=True)
    op.alter_column('regulatory_claim_rules', 'unit', existing_type=sa.String(length=30), nullable=True)

    op.create_check_constraint(
        'chk_claim_food_form',
        'regulatory_claim_rules',
        "food_form IN ('solid', 'liquid', 'both')"
    )
    op.create_check_constraint(
        'chk_claim_operator',
        'regulatory_claim_rules',
        "operator IS NULL OR operator IN ('LT', 'LTE', 'GT', 'GTE', 'EQ')"
    )
    op.create_check_constraint(
        'chk_claim_family',
        'regulatory_claim_rules',
        "claim_family IN ('NUTRIENT_CONTENT_CLAIM', 'NON_ADDITION_CLAIM')"
    )

    op.create_index('idx_rcr_claim_code', 'regulatory_claim_rules', ['claim_code'])
    op.create_index('idx_rcr_active', 'regulatory_claim_rules', ['is_active'])
    op.create_index('idx_rcr_family', 'regulatory_claim_rules', ['claim_family'])

    # -------------------------------------------------------------------------
    # 4. DEF-01: Table 15.1 Nutrient Threshold Rules
    # -------------------------------------------------------------------------
    op.create_table(
        'icmr_nutrient_threshold_rules',
        sa.Column('rule_id', sa.String(length=100), nullable=False),
        sa.Column('rule_code', sa.String(length=50), nullable=False),
        sa.Column('nutrient_code', sa.String(length=50), nullable=False),
        sa.Column('food_form', sa.String(length=20), nullable=False),
        sa.Column('threshold_value', sa.Numeric(precision=10, scale=3), nullable=False),
        sa.Column('operator', sa.String(length=10), nullable=False, server_default='GT'),
        sa.Column('measurement_basis', sa.String(length=30), nullable=False),
        sa.Column(
            'guideline_reference',
            sa.Text(),
            nullable=False,
            server_default='ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1'
        ),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.CheckConstraint("food_form IN ('solid', 'liquid')", name='chk_icmr_thresh_food_form'),
        sa.CheckConstraint("operator IN ('GT', 'GTE')", name='chk_icmr_thresh_operator'),
        sa.CheckConstraint("measurement_basis IN ('PER_100G', 'PER_100ML')", name='chk_icmr_thresh_basis'),
        sa.ForeignKeyConstraint(['nutrient_code'], ['nutrients.nutrient_code']),
        sa.PrimaryKeyConstraint('rule_id')
    )
    op.create_index('idx_icmr_thresh_nutrient', 'icmr_nutrient_threshold_rules', ['nutrient_code'])
    op.create_index('idx_icmr_thresh_active', 'icmr_nutrient_threshold_rules', ['is_active'])

    # -------------------------------------------------------------------------
    # 5. DEF-01: Table 15.2 Food Classification Matrix Rules
    # -------------------------------------------------------------------------
    op.create_table(
        'icmr_matrix_rules',
        sa.Column('matrix_id', sa.String(length=100), nullable=False),
        sa.Column('cell_code', sa.String(length=10), nullable=False),
        sa.Column('processing_group', sa.String(length=20), nullable=False),
        sa.Column('nutritional_category', sa.String(length=20), nullable=False),
        sa.Column('applicable_food_form', sa.String(length=20), nullable=False, server_default='solid'),
        sa.Column('is_upf', sa.Boolean(), nullable=False),
        sa.Column('is_hfss', sa.Boolean(), nullable=False),
        sa.Column('energy_min_kcal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('energy_max_kcal', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('processing_description', sa.Text(), nullable=False),
        sa.Column('nutritional_description', sa.Text(), nullable=False),
        sa.Column('consumer_guidance', sa.Text(), nullable=False),
        sa.Column(
            'guideline_reference',
            sa.Text(),
            nullable=False,
            server_default='ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2'
        ),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.CheckConstraint("cell_code IN ('A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3')", name='chk_icmr_matrix_cell'),
        sa.CheckConstraint("processing_group IN ('GROUP_A', 'GROUP_B', 'GROUP_C')", name='chk_icmr_matrix_group'),
        sa.CheckConstraint("nutritional_category IN ('CAT_1', 'CAT_2', 'CAT_3')", name='chk_icmr_matrix_cat'),
        sa.CheckConstraint("applicable_food_form IN ('solid', 'liquid')", name='chk_icmr_matrix_food_form'),
        sa.PrimaryKeyConstraint('matrix_id'),
        sa.UniqueConstraint('cell_code', name='uq_icmr_matrix_cell')
    )
    op.create_index('idx_icmr_matrix_group_cat', 'icmr_matrix_rules', ['processing_group', 'nutritional_category'])

    # -------------------------------------------------------------------------
    # 6. DEF-06: Enhance ingredient_rules table with reconciled rule types
    # -------------------------------------------------------------------------
    op.add_column(
        'ingredient_rules',
        sa.Column('target_food_category', sa.String(length=100), nullable=False, server_default='ALL')
    )
    op.add_column(
        'ingredient_rules',
        sa.Column('max_permitted_ppm', sa.Numeric(precision=10, scale=2), nullable=True)
    )
    op.add_column(
        'ingredient_rules',
        sa.Column('warning_statement', sa.Text(), nullable=True)
    )
    op.create_check_constraint(
        'chk_ingredient_rule_type',
        'ingredient_rules',
        "rule_type IN ('MANDATORY_LABEL_WARNING', 'MAX_PERMISSIBLE_LIMIT', 'POPULATION_PROHIBITION', 'SPECIAL_CONDITIONS', 'WARNING_MANDATE', 'MAX_LIMIT')"
    )
    op.create_index('idx_ir_ingredient', 'ingredient_rules', ['ingredient_code'])
    op.create_index('idx_ir_type', 'ingredient_rules', ['rule_type'])

    # -------------------------------------------------------------------------
    # 7. Safely Deprecate nutrition_interpretation_rules
    # -------------------------------------------------------------------------
    op.execute(
        "COMMENT ON TABLE nutrition_interpretation_rules IS '[DEPRECATED] Superseded by icmr_nutrient_threshold_rules & icmr_matrix_rules. Retained for rollback safety.'"
    )


def downgrade() -> None:
    # 7. Revert comment
    op.execute("COMMENT ON TABLE nutrition_interpretation_rules IS NULL")

    # 6. Revert ingredient_rules
    op.drop_index('idx_ir_type', table_name='ingredient_rules')
    op.drop_index('idx_ir_ingredient', table_name='ingredient_rules')
    op.drop_constraint('chk_ingredient_rule_type', 'ingredient_rules', type_='check')
    op.drop_column('ingredient_rules', 'warning_statement')
    op.drop_column('ingredient_rules', 'max_permitted_ppm')
    op.drop_column('ingredient_rules', 'target_food_category')

    # 5. Drop icmr_matrix_rules
    op.drop_index('idx_icmr_matrix_group_cat', table_name='icmr_matrix_rules')
    op.drop_table('icmr_matrix_rules')

    # 4. Drop icmr_nutrient_threshold_rules
    op.drop_index('idx_icmr_thresh_active', table_name='icmr_nutrient_threshold_rules')
    op.drop_index('idx_icmr_thresh_nutrient', table_name='icmr_nutrient_threshold_rules')
    op.drop_table('icmr_nutrient_threshold_rules')

    # 3. Revert regulatory_claim_rules
    op.drop_index('idx_rcr_family', table_name='regulatory_claim_rules')
    op.drop_index('idx_rcr_active', table_name='regulatory_claim_rules')
    op.drop_index('idx_rcr_claim_code', table_name='regulatory_claim_rules')
    op.drop_constraint('chk_claim_family', 'regulatory_claim_rules', type_='check')
    op.drop_constraint('chk_claim_operator', 'regulatory_claim_rules', type_='check')
    op.drop_constraint('chk_claim_food_form', 'regulatory_claim_rules', type_='check')

    op.alter_column('regulatory_claim_rules', 'unit', existing_type=sa.String(length=30), nullable=False)
    op.alter_column('regulatory_claim_rules', 'threshold_value', existing_type=sa.Numeric(precision=10, scale=3), nullable=False)
    op.alter_column('regulatory_claim_rules', 'operator', existing_type=sa.String(length=10), nullable=False)

    op.drop_column('regulatory_claim_rules', 'is_active')
    op.drop_column('regulatory_claim_rules', 'effective_to')
    op.drop_column('regulatory_claim_rules', 'effective_from')
    op.drop_column('regulatory_claim_rules', 'official_source_version')
    op.drop_column('regulatory_claim_rules', 'permitted_synonyms_schedule_ii')
    op.drop_column('regulatory_claim_rules', 'condition_expression')
    op.drop_column('regulatory_claim_rules', 'applicable_category')
    op.drop_column('regulatory_claim_rules', 'claim_family')
    op.drop_column('regulatory_claim_rules', 'claim_title')

    op.create_check_constraint(
        'chk_claim_food_form',
        'regulatory_claim_rules',
        "food_form IN ('solid', 'liquid')"
    )
    op.create_check_constraint(
        'chk_claim_operator',
        'regulatory_claim_rules',
        "operator IN ('LTE', 'GTE', 'EQ')"
    )

    # 2. Revert ingredients
    op.drop_constraint('chk_ingredient_sugar_class', 'ingredients', type_='check')
    op.drop_constraint('chk_ingredient_proc_class', 'ingredients', type_='check')
    op.drop_column('ingredients', 'classification_evidence')
    op.drop_column('ingredients', 'sugar_classification')
    op.drop_column('ingredients', 'processing_classification')

    # 1. Revert nutrients
    op.drop_column('nutrients', 'rdi_citation')
    op.drop_column('nutrients', 'fssai_standard_daily_rdi')
