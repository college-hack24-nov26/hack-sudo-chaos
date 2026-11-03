BEGIN;

-- Running downgrade 0003_seed_verified_rule_data -> 0002_enhance_rules

DELETE FROM ingredient_rules
    WHERE rule_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'ingredient_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'ingredient_rules';;

DELETE FROM regulatory_claim_rules
    WHERE claim_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'regulatory_claim_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'regulatory_claim_rules';;

DELETE FROM icmr_matrix_rules
    WHERE matrix_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'icmr_matrix_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'icmr_matrix_rules';;

DELETE FROM icmr_nutrient_threshold_rules
    WHERE rule_id IN (
        SELECT record_id FROM migration_seed_ownership
        WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'icmr_nutrient_threshold_rules'
    );
    DELETE FROM migration_seed_ownership
    WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'icmr_nutrient_threshold_rules';;

DO $cleanup_ing$
    DECLARE
        r RECORD;
        blocked_count INT := 0;
    BEGIN
        FOR r IN (
            SELECT record_id FROM migration_seed_ownership
            WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'ingredients'
        ) LOOP
            IF EXISTS (SELECT 1 FROM product_ingredients WHERE ingredient_code = r.record_id) OR
               EXISTS (SELECT 1 FROM ingredient_rules WHERE ingredient_code = r.record_id) THEN
                RAISE WARNING 'Cleanup blocked: ingredient "%" is referenced by dependent data and will be preserved.', r.record_id;
                blocked_count := blocked_count + 1;
            ELSE
                DELETE FROM ingredients WHERE ingredient_code = r.record_id;
                DELETE FROM migration_seed_ownership
                WHERE migration_revision = '0003_seed_verified_rule_data'
                  AND target_table = 'ingredients'
                  AND record_id = r.record_id;
            END IF;
        END LOOP;
        IF blocked_count > 0 THEN
            RAISE NOTICE 'Preserved % ingredient(s) due to active foreign key references.', blocked_count;
        END IF;
    END $cleanup_ing$;;

DO $cleanup_nut$
    DECLARE
        r RECORD;
        blocked_count INT := 0;
    BEGIN
        FOR r IN (
            SELECT record_id FROM migration_seed_ownership
            WHERE migration_revision = '0003_seed_verified_rule_data' AND target_table = 'nutrients'
        ) LOOP
            IF EXISTS (SELECT 1 FROM product_nutrients WHERE nutrient_code = r.record_id) OR
               EXISTS (SELECT 1 FROM icmr_nutrient_threshold_rules WHERE nutrient_code = r.record_id) OR
               EXISTS (SELECT 1 FROM nutrition_interpretation_rules WHERE nutrient_code = r.record_id) THEN
                RAISE WARNING 'Cleanup blocked: nutrient "%" is referenced by dependent data and will be preserved.', r.record_id;
                blocked_count := blocked_count + 1;
            ELSE
                DELETE FROM nutrients WHERE nutrient_code = r.record_id;
                DELETE FROM migration_seed_ownership
                WHERE migration_revision = '0003_seed_verified_rule_data'
                  AND target_table = 'nutrients'
                  AND record_id = r.record_id;
            END IF;
        END LOOP;
        IF blocked_count > 0 THEN
            RAISE NOTICE 'Preserved % nutrient(s) due to active foreign key references.', blocked_count;
        END IF;
    END $cleanup_nut$;;

DO $drop_tracker$
    BEGIN
        IF (SELECT COUNT(*) FROM migration_seed_ownership) = 0 THEN
            DROP TABLE migration_seed_ownership;
            RAISE NOTICE 'migration_seed_ownership dropped (all owned records cleanly removed).';
        ELSE
            RAISE NOTICE 'migration_seed_ownership retained (uncleaned/blocked records remain for audit telemetry).';
        END IF;
    END $drop_tracker$;;

UPDATE alembic_version SET version_num='0002_enhance_rules' WHERE alembic_version.version_num = '0003_seed_verified_rule_data';

COMMIT;

