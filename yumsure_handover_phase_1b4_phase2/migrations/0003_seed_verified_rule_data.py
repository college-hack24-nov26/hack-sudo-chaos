"""Seed verified regulatory rule data for Phase 1B.4 & Phase 2.

Revision ID: 0003_seed_verified_rule_data
Revises: 0002_enhance_rules
Create Date: 2026-11-03 21:30:00.000000

Safety Guarantees for Tejas's Integration:
1. Migration Ownership Tracking:
   Tracks inserted rows via `migration_seed_ownership` table using PostgreSQL CTEs:
   `WITH ins AS (INSERT ... ON CONFLICT DO NOTHING RETURNING pk) INSERT INTO migration_seed_ownership ... SELECT ... FROM ins;`
   If a record already existed prior to migration 0003, ON CONFLICT DO NOTHING activates and RETURNING produces 0 rows;
   therefore, no ownership entry is created, guaranteeing pre-existing data is NEVER claimed or deleted.
2. Downgrade Safety & Strict Reverse FK Order:
   Rollback strictly deletes rows recorded in `migration_seed_ownership` for this revision in reverse dependency order:
   `ingredient_rules` -> `regulatory_claim_rules` -> `icmr_matrix_rules` -> `icmr_nutrient_threshold_rules` -> `ingredients` -> `nutrients`.
3. Deterministic Foreign Key Protection on Canonical Lookup Tables:
   Deletions from canonical lookup tables (`ingredients`, `nutrients`) inspect all referencing tables:
   - For `ingredients`: `product_ingredients` and remaining `ingredient_rules`.
   - For `nutrients`: `product_nutrients`, `icmr_nutrient_threshold_rules`, and `nutrition_interpretation_rules`.
   If dependent application data or child rules reference an owned canonical record:
   - The deletion of that record is safely blocked and preserved.
   - An explicit WARNING is logged: `Cleanup blocked: <target> '<id>' is referenced by dependent data and will be preserved.`
   - The ownership tracking record in `migration_seed_ownership` is retained, keeping full telemetry.
4. Lifecycle of Tracking Table:
   `migration_seed_ownership` is created during upgrade. During downgrade, if all owned records are cleanly removed
   and no other uncleaned/blocked records remain, the tracking table is dropped; otherwise, it is retained for audit telemetry.
"""

import json
import os
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003_seed_verified_rule_data'
down_revision: Union[str, None] = '0002_enhance_rules'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _load_seed(filename: str):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.normpath(os.path.join(base_dir, '..', '..', 'app', 'data', 'seeds', filename))
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _sql_str(val):
    if val is None:
        return "NULL"
    escaped = str(val).replace("'", "''")
    return f"'{escaped}'"


def _sql_num(val):
    if val is None:
        return "NULL"
    return str(val)


def _sql_bool(val):
    if val is None:
        return "NULL"
    return "TRUE" if val else "FALSE"


def _sql_json(val):
    if val is None:
        return "NULL"
    s = json.dumps(val, ensure_ascii=False)
    escaped = s.replace("'", "''")
    return f"'{escaped}'::jsonb"


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # 0. Migration Seed Ownership Tracking Table
    # -------------------------------------------------------------------------
    op.execute(sa.text("""
    CREATE TABLE IF NOT EXISTS migration_seed_ownership (
        id SERIAL PRIMARY KEY,
        migration_revision VARCHAR(100) NOT NULL,
        target_table VARCHAR(100) NOT NULL,
        record_id VARCHAR(100) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT uq_migration_seed_ownership UNIQUE (migration_revision, target_table, record_id)
    );
    """.strip()))

    # -------------------------------------------------------------------------
    # 1. Seed Canonical Nutrients (Safe: ON CONFLICT DO NOTHING with CTE tracking)
    # -------------------------------------------------------------------------
    nutrients = _load_seed('canonical_nutrients_seed.json')
    for n in nutrients:
        sql = f"""
        WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                {_sql_str(n['nutrient_code'])},
                {_sql_str(n['display_name'])},
                {_sql_str(n['standard_unit'])},
                {_sql_bool(n['is_fssai_mandatory'])},
                {_sql_num(n.get('fssai_standard_daily_rdi'))},
                {_sql_str(n.get('rdi_citation'))}
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '{revision}', 'nutrients', pk FROM ins;
        """
        op.execute(sa.text(sql.strip()))

    # -------------------------------------------------------------------------
    # 2. Seed Canonical Ingredients (Safe: ON CONFLICT DO NOTHING with CTE tracking)
    # -------------------------------------------------------------------------
    ingredients = _load_seed('canonical_ingredients_seed.json')
    for ing in ingredients:
        sql = f"""
        WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                {_sql_str(ing['ingredient_code'])},
                {_sql_str(ing['canonical_name'])},
                {_sql_str(ing.get('ins_number'))},
                {_sql_str(ing['category'])},
                {_sql_bool(ing.get('is_fssai_major_allergen', False))},
                {_sql_str(ing.get('functional_description'))},
                {_sql_str(ing.get('processing_classification', 'UNKNOWN'))},
                {_sql_str(ing.get('sugar_classification', 'UNKNOWN'))},
                {_sql_str(ing.get('classification_evidence'))}
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '{revision}', 'ingredients', pk FROM ins;
        """
        op.execute(sa.text(sql.strip()))

    # -------------------------------------------------------------------------
    # 3. Seed ICMR Table 15.1 Nutrient Threshold Rules (Safe: ON CONFLICT DO NOTHING with CTE tracking)
    # -------------------------------------------------------------------------
    t151_rules = _load_seed('icmr_table_15_1_seed.json')
    for r in t151_rules:
        sql = f"""
        WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                {_sql_str(r['rule_id'])},
                {_sql_str(r['rule_code'])},
                {_sql_str(r['nutrient_code'])},
                {_sql_str(r['food_form'])},
                {_sql_num(r['threshold_value'])},
                {_sql_str(r.get('operator', 'GT'))},
                {_sql_str(r['measurement_basis'])},
                {_sql_str(r.get('guideline_reference', 'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1'))},
                {_sql_bool(r.get('is_active', True))}
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '{revision}', 'icmr_nutrient_threshold_rules', pk FROM ins;
        """
        op.execute(sa.text(sql.strip()))

    # -------------------------------------------------------------------------
    # 4. Seed ICMR Table 15.2 Food Classification Matrix Rules (Safe: ON CONFLICT DO NOTHING with CTE tracking)
    # -------------------------------------------------------------------------
    t152_rules = _load_seed('icmr_table_15_2_seed.json')
    for m in t152_rules:
        sql = f"""
        WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                {_sql_str(m['matrix_id'])},
                {_sql_str(m['cell_code'])},
                {_sql_str(m['processing_group'])},
                {_sql_str(m['nutritional_category'])},
                {_sql_str(m.get('applicable_food_form', 'solid'))},
                {_sql_bool(m['is_upf'])},
                {_sql_bool(m['is_hfss'])},
                {_sql_num(m.get('energy_min_kcal'))},
                {_sql_num(m.get('energy_max_kcal'))},
                {_sql_str(m['processing_description'])},
                {_sql_str(m['nutritional_description'])},
                {_sql_str(m['consumer_guidance'])},
                {_sql_str(m.get('guideline_reference', 'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2'))},
                {_sql_bool(m.get('is_active', True))}
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '{revision}', 'icmr_matrix_rules', pk FROM ins;
        """
        op.execute(sa.text(sql.strip()))

    # -------------------------------------------------------------------------
    # 5. Seed FSSAI Schedule I Statutory Claims (Safe: ON CONFLICT DO NOTHING with CTE tracking)
    # -------------------------------------------------------------------------
    claims = _load_seed('fssai_schedule_i_claims_seed.json')
    for c in claims:
        sql = f"""
        WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                {_sql_str(c['claim_id'])},
                {_sql_str(c['claim_code'])},
                {_sql_str(c.get('claim_title', ''))},
                {_sql_str(c.get('claim_family', 'NUTRIENT_CONTENT_CLAIM'))},
                {_sql_str(c['food_form'])},
                {_sql_str(c.get('applicable_category', 'ALL'))},
                {_sql_str(c.get('operator'))},
                {_sql_num(c.get('threshold_value'))},
                {_sql_str(c.get('unit'))},
                {_sql_json(c.get('condition_expression'))},
                {_sql_json(c.get('permitted_synonyms_schedule_ii', []))},
                {_sql_str(c['fssai_regulation_reference'])},
                {_sql_str(c.get('official_source_version', 'Version III (04-10-2022)'))},
                {_sql_str(c.get('effective_from', '2019-07-01'))}::date,
                {_sql_bool(c.get('is_active', True))},
                {_sql_str(c.get('consumer_explanation', ''))}
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '{revision}', 'regulatory_claim_rules', pk FROM ins;
        """
        op.execute(sa.text(sql.strip()))

    # -------------------------------------------------------------------------
    # 6. Seed Ingredient Warning and Additive Rules (Safe: ON CONFLICT DO NOTHING with CTE tracking)
    # -------------------------------------------------------------------------
    ir_rules = _load_seed('ingredient_rules_seed.json')
    for ir in ir_rules:
        sql = f"""
        WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                {_sql_str(ir['rule_id'])},
                {_sql_str(ir['ingredient_code'])},
                {_sql_str(ir['rule_type'])},
                {_sql_str(ir.get('target_food_category', 'ALL'))},
                {_sql_num(ir.get('max_permitted_ppm'))},
                {_sql_str(ir.get('warning_statement'))},
                {_sql_str(ir.get('condition_expression'))},
                {_sql_str(ir['regulatory_reference'])},
                {_sql_str(ir.get('consumer_guidance', ''))}
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '{revision}', 'ingredient_rules', pk FROM ins;
        """
        op.execute(sa.text(sql.strip()))


def downgrade() -> None:
    # -------------------------------------------------------------------------
    # 1. Delete ingredient rules strictly owned by 0003
    # -------------------------------------------------------------------------
    sql_ir = f"""
    DELETE FROM ingredient_rules
    WHERE rule_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '{revision}' AND target_table = 'ingredient_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '{revision}' AND target_table = 'ingredient_rules';
    """
    op.execute(sa.text(sql_ir.strip()))

    # -------------------------------------------------------------------------
    # 2. Delete regulatory claim rules strictly owned by 0003
    # -------------------------------------------------------------------------
    sql_claims = f"""
    DELETE FROM regulatory_claim_rules
    WHERE claim_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '{revision}' AND target_table = 'regulatory_claim_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '{revision}' AND target_table = 'regulatory_claim_rules';
    """
    op.execute(sa.text(sql_claims.strip()))

    # -------------------------------------------------------------------------
    # 3. Delete Table 15.2 matrix rules strictly owned by 0003
    # -------------------------------------------------------------------------
    sql_t152 = f"""
    DELETE FROM icmr_matrix_rules
    WHERE matrix_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '{revision}' AND target_table = 'icmr_matrix_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '{revision}' AND target_table = 'icmr_matrix_rules';
    """
    op.execute(sa.text(sql_t152.strip()))

    # -------------------------------------------------------------------------
    # 4. Delete Table 15.1 threshold rules strictly owned by 0003
    # -------------------------------------------------------------------------
    sql_t151 = f"""
    DELETE FROM icmr_nutrient_threshold_rules
    WHERE rule_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '{revision}' AND target_table = 'icmr_nutrient_threshold_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '{revision}' AND target_table = 'icmr_nutrient_threshold_rules';
    """
    op.execute(sa.text(sql_t151.strip()))

    # -------------------------------------------------------------------------
    # 5. Delete ingredients strictly owned by 0003 with FK checking and explicit warning
    # -------------------------------------------------------------------------
    sql_ing = f"""
    DO $cleanup_ing$
    DECLARE
        r RECORD;
        blocked_count INT := 0;
    BEGIN
        FOR r IN (
            SELECT record_id FROM migration_seed_ownership
            WHERE migration_revision = '{revision}' AND target_table = 'ingredients'
        ) LOOP
            IF EXISTS (SELECT 1 FROM product_ingredients WHERE ingredient_code = r.record_id) OR
               EXISTS (SELECT 1 FROM ingredient_rules WHERE ingredient_code = r.record_id) THEN
                RAISE WARNING 'Cleanup blocked: ingredient "%" is referenced by dependent data and will be preserved.', r.record_id;
                blocked_count := blocked_count + 1;
            ELSE
                DELETE FROM ingredients WHERE ingredient_code = r.record_id;
                DELETE FROM migration_seed_ownership
                WHERE migration_revision = '{revision}'
                  AND target_table = 'ingredients'
                  AND record_id = r.record_id;
            END IF;
        END LOOP;
        IF blocked_count > 0 THEN
            RAISE NOTICE 'Preserved % ingredient(s) due to active foreign key references.', blocked_count;
        END IF;
    END $cleanup_ing$;
    """
    op.execute(sa.text(sql_ing.strip()))

    # -------------------------------------------------------------------------
    # 6. Delete nutrients strictly owned by 0003 with FK checking and explicit warning
    # -------------------------------------------------------------------------
    sql_nut = f"""
    DO $cleanup_nut$
    DECLARE
        r RECORD;
        blocked_count INT := 0;
    BEGIN
        FOR r IN (
            SELECT record_id FROM migration_seed_ownership
            WHERE migration_revision = '{revision}' AND target_table = 'nutrients'
        ) LOOP
            IF EXISTS (SELECT 1 FROM product_nutrients WHERE nutrient_code = r.record_id) OR
               EXISTS (SELECT 1 FROM icmr_nutrient_threshold_rules WHERE nutrient_code = r.record_id) OR
               EXISTS (SELECT 1 FROM nutrition_interpretation_rules WHERE nutrient_code = r.record_id) THEN
                RAISE WARNING 'Cleanup blocked: nutrient "%" is referenced by dependent data and will be preserved.', r.record_id;
                blocked_count := blocked_count + 1;
            ELSE
                DELETE FROM nutrients WHERE nutrient_code = r.record_id;
                DELETE FROM migration_seed_ownership
                WHERE migration_revision = '{revision}'
                  AND target_table = 'nutrients'
                  AND record_id = r.record_id;
            END IF;
        END LOOP;
        IF blocked_count > 0 THEN
            RAISE NOTICE 'Preserved % nutrient(s) due to active foreign key references.', blocked_count;
        END IF;
    END $cleanup_nut$;
    """
    op.execute(sa.text(sql_nut.strip()))

    # -------------------------------------------------------------------------
    # 7. Drop tracking table if completely empty, or retain if uncleaned records remain
    # -------------------------------------------------------------------------
    sql_drop_tracker = """
    DO $drop_tracker$
    BEGIN
        IF (SELECT COUNT(*) FROM migration_seed_ownership) = 0 THEN
            DROP TABLE migration_seed_ownership;
            RAISE NOTICE 'migration_seed_ownership dropped (all owned records cleanly removed).';
        ELSE
            RAISE NOTICE 'migration_seed_ownership retained (uncleaned/blocked records remain for audit telemetry).';
        END IF;
    END $drop_tracker$;
    """
    op.execute(sa.text(sql_drop_tracker.strip()))
