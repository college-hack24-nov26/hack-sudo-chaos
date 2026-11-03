BEGIN;

-- Running upgrade 0002_enhance_rules -> 0003_seed_verified_rule_data

CREATE TABLE IF NOT EXISTS migration_seed_ownership (
        id SERIAL PRIMARY KEY,
        migration_revision VARCHAR(100) NOT NULL,
        target_table VARCHAR(100) NOT NULL,
        record_id VARCHAR(100) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT uq_migration_seed_ownership UNIQUE (migration_revision, target_table, record_id)
    );;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'energy',
                'Energy',
                'kcal',
                TRUE,
                2000.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'protein',
                'Protein',
                'g',
                TRUE,
                54.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'carbohydrates',
                'Carbohydrates',
                'g',
                TRUE,
                300.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'total_sugars',
                'Total Sugars',
                'g',
                TRUE,
                NULL,
                NULL
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'added_sugars',
                'Added Sugars',
                'g',
                TRUE,
                50.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'total_fat',
                'Total Fat',
                'g',
                TRUE,
                67.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'saturated_fat',
                'Saturated Fat',
                'g',
                TRUE,
                22.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'trans_fat',
                'Trans Fat',
                'g',
                TRUE,
                2.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'sodium',
                'Sodium',
                'mg',
                TRUE,
                2000.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'dietary_fibre',
                'Dietary Fibre',
                'g',
                FALSE,
                30.0,
                'FSSAI (Labelling and Display) Regulations 2020, Reg 5(3)(b)'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO nutrients (
                nutrient_code, display_name, standard_unit, is_fssai_mandatory, fssai_standard_daily_rdi, rdi_citation
            ) VALUES (
                'added_fat',
                'Added Fat',
                'g',
                FALSE,
                25.0,
                'ICMR-NIN DGI 2024 Reference'
            ) ON CONFLICT (nutrient_code) DO NOTHING
            RETURNING nutrient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'nutrients', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                'ins_951_aspartame',
                'Aspartame',
                '951',
                'SWEETENER',
                FALSE,
                'Non-nutritive intense artificial sweetener, 200x sucrose potency.',
                'FUNCTIONAL_ADDITIVE',
                'NON_NUTRITIVE_SWEETENER',
                'JECFA Evaluation; FSSAI Labelling Schedule II Entry 1'
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredients', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                'ins_965_maltitol',
                'Maltitol',
                '965',
                'SWEETENER',
                FALSE,
                'Polyol sugar alcohol sweetener with bulk sweetening properties.',
                'FUNCTIONAL_ADDITIVE',
                'POLYOL',
                'FSSAI Labelling Schedule II Entry 4'
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredients', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                'ins_420_sorbitol',
                'Sorbitol',
                '420',
                'SWEETENER',
                FALSE,
                'Polyol sugar alcohol humectant and sweetener.',
                'FUNCTIONAL_ADDITIVE',
                'POLYOL',
                'FSSAI Labelling Schedule II Entry 4'
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredients', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                'caffeine',
                'Caffeine',
                NULL,
                'OTHER',
                FALSE,
                'Central nervous system stimulant used in energy beverages.',
                'FUNCTIONAL_ADDITIVE',
                'NOT_SUGAR',
                'FSSAI Food Additives Regulations 2011 Appendix A Table 3'
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredients', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                'ins_211_sodium_benzoate',
                'Sodium Benzoate',
                '211',
                'PRESERVATIVE',
                FALSE,
                'Chemical antimicrobial preservative active against yeasts and bacteria in acidic foods.',
                'FUNCTIONAL_ADDITIVE',
                'NOT_SUGAR',
                'FSSAI Additives 2011 Appendix A Table 3'
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredients', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredients (
                ingredient_code, canonical_name, ins_number, category, is_fssai_major_allergen,
                functional_description, processing_classification, sugar_classification, classification_evidence
            ) VALUES (
                'ins_202_potassium_sorbate',
                'Potassium Sorbate',
                '202',
                'PRESERVATIVE',
                FALSE,
                'Chemical preservative against moulds and yeasts in foods.',
                'FUNCTIONAL_ADDITIVE',
                'NOT_SUGAR',
                'FSSAI Additives 2011 Appendix A Table 3'
            ) ON CONFLICT (ingredient_code) DO NOTHING
            RETURNING ingredient_code AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredients', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_added_sugar_solid',
                'HFSS_THRESHOLD_ADDED_SUGAR_SOLID',
                'added_sugars',
                'solid',
                3.0,
                'GT',
                'PER_100G',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_added_sugar_liquid',
                'HFSS_THRESHOLD_ADDED_SUGAR_LIQUID',
                'added_sugars',
                'liquid',
                2.0,
                'GT',
                'PER_100ML',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_salt_solid',
                'HFSS_THRESHOLD_SALT_SOLID',
                'sodium',
                'solid',
                625.0,
                'GT',
                'PER_100G',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_salt_liquid',
                'HFSS_THRESHOLD_SALT_LIQUID',
                'sodium',
                'liquid',
                175.0,
                'GT',
                'PER_100ML',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_added_fat_solid',
                'HFSS_THRESHOLD_ADDED_FAT_SOLID',
                'added_fat',
                'solid',
                4.2,
                'GT',
                'PER_100G',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_added_fat_liquid',
                'HFSS_THRESHOLD_ADDED_FAT_LIQUID',
                'added_fat',
                'liquid',
                1.5,
                'GT',
                'PER_100ML',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_energy_solid',
                'HFSS_THRESHOLD_ENERGY_SOLID',
                'energy',
                'solid',
                250.0,
                'GT',
                'PER_100G',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_nutrient_threshold_rules (
                rule_id, rule_code, nutrient_code, food_form, threshold_value,
                operator, measurement_basis, guideline_reference, is_active
            ) VALUES (
                'icmr_15_1_energy_liquid',
                'HFSS_THRESHOLD_ENERGY_LIQUID',
                'energy',
                'liquid',
                70.0,
                'GT',
                'PER_100ML',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.1, p. 96',
                TRUE
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_nutrient_threshold_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_a1',
                'A1',
                'GROUP_A',
                'CAT_1',
                'solid',
                FALSE,
                FALSE,
                NULL,
                250.0,
                'Minimally processed fresh or frozen foods (e.g. cut fruits, raw vegetables, boiled whole legumes).',
                'Low calorific density (<=250 kcal/100g) with natural nutrient matrix.',
                'Recommended core of a healthy diet. Wholesome and nutrient-rich.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_a2',
                'A2',
                'GROUP_A',
                'CAT_2',
                'solid',
                FALSE,
                TRUE,
                250.0,
                500.0,
                'Minimally processed natural whole foods with moderate natural energy density (e.g. dried whole grains, dried fruits, plain roasted oilseeds).',
                'Moderate calorific density (>250 to 500 kcal/100g) without industrial deconstruction.',
                'Wholesome food. Consume as part of balanced meals with portion awareness.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_a3',
                'A3',
                'GROUP_A',
                'CAT_3',
                'solid',
                FALSE,
                TRUE,
                500.0,
                NULL,
                'Minimally processed natural high-energy foods (e.g. whole tree nuts, dry oilseeds).',
                'High calorific density (>500 kcal/100g) due to natural intrinsic oils.',
                'Nutrient-dense whole food. Consume in controlled portions (e.g. 15-30g daily).',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_b1',
                'B1',
                'GROUP_B',
                'CAT_1',
                'solid',
                FALSE,
                FALSE,
                NULL,
                250.0,
                'Processed culinary ingredients or cooked foods using culinary additives (e.g. salted canned vegetables, tomato puree with salt/citric acid).',
                'Low calorific density (<=250 kcal/100g).',
                'Suitable culinary ingredient. Monitor added salt or culinary seasoning.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_b2',
                'B2',
                'GROUP_B',
                'CAT_2',
                'solid',
                FALSE,
                TRUE,
                250.0,
                500.0,
                'Processed traditional foods cooked with culinary fat or sugar (e.g. freshly baked plain bread, homemade snack mixes).',
                'Moderate calorific density (>250 to 500 kcal/100g) due to added culinary fats/sugar.',
                'Consume in moderation. Limit frequency of foods with added culinary sugar and fat.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_b3',
                'B3',
                'GROUP_B',
                'CAT_3',
                'solid',
                FALSE,
                TRUE,
                500.0,
                NULL,
                'Culinary fats/oils or deep-fried traditional foods (e.g. pure ghee, cold-pressed vegetable oil, traditional savouries).',
                'High calorific density (>500 kcal/100g).',
                'High calorie food/fat. Use sparingly as cooking medium in limited amounts.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 97',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_c1',
                'C1',
                'GROUP_C',
                'CAT_1',
                'solid',
                TRUE,
                FALSE,
                NULL,
                250.0,
                'Ultra-processed industrial formulation containing cosmetic additives, emulsifiers, or intense sweeteners, but formulated to be low in energy (e.g. reconstituted low-calorie textured snacks, diet solid gel desserts).',
                'Low calorific density (<=250 kcal/100g), non-HFSS by calorie criteria.',
                'Ultra-processed food. Non-HFSS by energy criteria, but consume rarely due to industrial processing and synthetic additives.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_c2',
                'C2',
                'GROUP_C',
                'CAT_2',
                'solid',
                TRUE,
                TRUE,
                250.0,
                500.0,
                'Ultra-processed food with industrial deconstruction and cosmetic additives (e.g. reconstituted breakfast cereals with flavourings, commercial biscuits, snack bars).',
                'Moderate calorific density (>250 to 500 kcal/100g) combined with ultra-processing.',
                'Ultra-processed and HFSS. Limit consumption; linked to metabolic health risks.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO icmr_matrix_rules (
                matrix_id, cell_code, processing_group, nutritional_category, applicable_food_form,
                is_upf, is_hfss, energy_min_kcal, energy_max_kcal,
                processing_description, nutritional_description, consumer_guidance,
                guideline_reference, is_active
            ) VALUES (
                'icmr_matrix_c3',
                'C3',
                'GROUP_C',
                'CAT_3',
                'solid',
                TRUE,
                TRUE,
                500.0,
                NULL,
                'Ultra-processed food of highest concern: industrial matrix deconstruction, cosmetic additives, and high fat/sugar content (e.g. commercial extruded potato chips, chocolate confectionery, filled cream biscuits).',
                'High calorific density (>500 kcal/100g) driven by industrial fats and refined carbohydrates.',
                'High-risk UPF and HFSS food. Avoid or consume very rarely.',
                'ICMR-NIN Dietary Guidelines for Indians (2024), Guideline 15, Table 15.2, p. 98',
                TRUE
            ) ON CONFLICT (matrix_id) DO NOTHING
            RETURNING matrix_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'icmr_matrix_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_trans_fat_free_solid',
                'TRANS_FAT_FREE',
                'Trans Fat Free (Solids)',
                'NUTRIENT_CONTENT_CLAIM',
                'solid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "trans_fat", "operator": "LT", "threshold_value": 0.2, "measurement_basis": "PER_100G", "food_form": "solid"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 1.5, "measurement_basis": "PER_100G", "food_form": "solid"}, {"type": "ENERGY_PERCENTAGE", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 10.0, "measurement_basis": "PCT_TOTAL_ENERGY"}]}'::jsonb,
                '["Trans Fat Free", "Zero Trans Fat", "Free of Trans Fat", "No Trans Fat"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains strictly less than 0.2g trans fat per 100g, and saturated fat not exceeding 1.5g/100g and 10% of total energy.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_trans_fat_free_liquid',
                'TRANS_FAT_FREE',
                'Trans Fat Free (Liquids)',
                'NUTRIENT_CONTENT_CLAIM',
                'liquid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "trans_fat", "operator": "LT", "threshold_value": 0.2, "measurement_basis": "PER_100ML", "food_form": "liquid"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 0.75, "measurement_basis": "PER_100ML", "food_form": "liquid"}, {"type": "ENERGY_PERCENTAGE", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 10.0, "measurement_basis": "PCT_TOTAL_ENERGY"}]}'::jsonb,
                '["Trans Fat Free", "Zero Trans Fat", "Free of Trans Fat", "No Trans Fat"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains strictly less than 0.2g trans fat per 100ml, and saturated fat not exceeding 0.75g/100ml and 10% of total energy.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_low_saturated_fat_solid',
                'LOW_SATURATED_FAT',
                'Low Saturated Fat (Solids)',
                'NUTRIENT_CONTENT_CLAIM',
                'solid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 1.5, "measurement_basis": "PER_100G", "food_form": "solid"}, {"type": "ENERGY_PERCENTAGE", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 10.0, "measurement_basis": "PCT_TOTAL_ENERGY"}]}'::jsonb,
                '["Low in Saturated Fat", "Little Saturated Fat"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(c)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains saturated fat not exceeding 1.5g per 100g and not more than 10% of total energy.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_low_saturated_fat_liquid',
                'LOW_SATURATED_FAT',
                'Low Saturated Fat (Liquids)',
                'NUTRIENT_CONTENT_CLAIM',
                'liquid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 0.75, "measurement_basis": "PER_100ML", "food_form": "liquid"}, {"type": "ENERGY_PERCENTAGE", "nutrient_code": "saturated_fat", "operator": "LTE", "threshold_value": 10.0, "measurement_basis": "PCT_TOTAL_ENERGY"}]}'::jsonb,
                '["Low in Saturated Fat", "Little Saturated Fat"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 4(c)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains saturated fat not exceeding 0.75g per 100ml and not more than 10% of total energy.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_source_of_protein_solid',
                'SOURCE_OF_PROTEIN',
                'Source of Protein (Solids)',
                'NUTRIENT_CONTENT_CLAIM',
                'solid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "OR", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 5.4, "measurement_basis": "PER_100G", "food_form": "solid"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 2.7, "measurement_basis": "PER_100KCAL", "food_form": "both"}]}'::jsonb,
                '["Provides Protein", "With Protein", "Contains Protein"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(a)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains not less than 5.4g protein per 100g (10% of 54g RDI) or 2.7g per 100 kcal.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_source_of_protein_liquid',
                'SOURCE_OF_PROTEIN',
                'Source of Protein (Liquids)',
                'NUTRIENT_CONTENT_CLAIM',
                'liquid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "OR", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 2.7, "measurement_basis": "PER_100ML", "food_form": "liquid"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 2.7, "measurement_basis": "PER_100KCAL", "food_form": "both"}]}'::jsonb,
                '["Provides Protein", "With Protein", "Contains Protein"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(a)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains not less than 2.7g protein per 100ml (5% of 54g RDI) or 2.7g per 100 kcal.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_high_protein_solid',
                'HIGH_PROTEIN',
                'High Protein (Solids)',
                'NUTRIENT_CONTENT_CLAIM',
                'solid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "OR", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 10.8, "measurement_basis": "PER_100G", "food_form": "solid"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 5.4, "measurement_basis": "PER_100KCAL", "food_form": "both"}]}'::jsonb,
                '["Rich in Protein", "Protein Rich", "Excellent Source of Protein"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains not less than 10.8g protein per 100g (20% of 54g RDI) or 5.4g per 100 kcal.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_high_protein_liquid',
                'HIGH_PROTEIN',
                'High Protein (Liquids)',
                'NUTRIENT_CONTENT_CLAIM',
                'liquid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "OR", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 5.4, "measurement_basis": "PER_100ML", "food_form": "liquid"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "protein", "operator": "GTE", "threshold_value": 5.4, "measurement_basis": "PER_100KCAL", "food_form": "both"}]}'::jsonb,
                '["Rich in Protein", "Protein Rich", "Excellent Source of Protein"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 5(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains not less than 5.4g protein per 100ml (10% of 54g RDI) or 5.4g per 100 kcal.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_source_of_dietary_fibre',
                'SOURCE_OF_DIETARY_FIBRE',
                'Source of Dietary Fibre',
                'NUTRIENT_CONTENT_CLAIM',
                'both',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "OR", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "dietary_fibre", "operator": "GTE", "threshold_value": 3.0, "measurement_basis": "PER_100G", "food_form": "both"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "dietary_fibre", "operator": "GTE", "threshold_value": 1.5, "measurement_basis": "PER_100KCAL", "food_form": "both"}]}'::jsonb,
                '["Provides Fibre", "Contains Fibre", "With Fibre"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 6(a)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains not less than 3.0g dietary fibre per 100g or 1.5g per 100 kcal.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_high_dietary_fibre',
                'HIGH_DIETARY_FIBRE',
                'High Dietary Fibre',
                'NUTRIENT_CONTENT_CLAIM',
                'both',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "OR", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "dietary_fibre", "operator": "GTE", "threshold_value": 6.0, "measurement_basis": "PER_100G", "food_form": "both"}, {"type": "NUTRIENT_THRESHOLD", "nutrient_code": "dietary_fibre", "operator": "GTE", "threshold_value": 3.0, "measurement_basis": "PER_100KCAL", "food_form": "both"}]}'::jsonb,
                '["Rich in Fibre", "Excellent Source of Fibre"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 6(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains not less than 6.0g dietary fibre per 100g or 3.0g per 100 kcal.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_low_sugars_solid',
                'LOW_SUGARS',
                'Low Sugars (Solids)',
                'NUTRIENT_CONTENT_CLAIM',
                'solid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "total_sugars", "operator": "LTE", "threshold_value": 5.0, "measurement_basis": "PER_100G", "food_form": "solid"}]}'::jsonb,
                '["Low Sugar", "Little Sugar"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 3(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains total sugars not exceeding 5.0g per 100g.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_low_sugars_liquid',
                'LOW_SUGARS',
                'Low Sugars (Liquids)',
                'NUTRIENT_CONTENT_CLAIM',
                'liquid',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "total_sugars", "operator": "LTE", "threshold_value": 2.5, "measurement_basis": "PER_100ML", "food_form": "liquid"}]}'::jsonb,
                '["Low Sugar", "Little Sugar"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 3(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains total sugars not exceeding 2.5g per 100ml.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_no_added_sugars',
                'NO_ADDED_SUGARS',
                'No Added Sugars',
                'NON_ADDITION_CLAIM',
                'both',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "added_sugars", "operator": "LTE", "threshold_value": 0.0, "measurement_basis": "PER_100G", "food_form": "both"}, {"type": "INGREDIENT_CHECK", "ingredient_criteria": {"disallowed_sugar_classes": ["ADDED_FREE_SUGAR", "SUGAR_SUBSTITUTE_SWEETENER"], "allow_intrinsic_sugars": true, "mandatory_disclosure_required": "CONTAINS NATURALLY OCCURRING SUGARS"}}]}'::jsonb,
                '["No Added Sugar", "Without Added Sugar", "Zero Added Sugar"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Regulation 6(1) & Schedule II',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains zero added sugars, no ingredients replacing sugar sweetness, and requires ''CONTAINS NATURALLY OCCURRING SUGARS'' disclosure if natural sugars are present.'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO regulatory_claim_rules (
                claim_id, claim_code, claim_title, claim_family, food_form, applicable_category,
                operator, threshold_value, unit,
                condition_expression, permitted_synonyms_schedule_ii,
                fssai_regulation_reference, official_source_version, effective_from, is_active,
                consumer_explanation
            ) VALUES (
                'fssai_claim_low_sodium',
                'LOW_SODIUM',
                'Low Sodium / Low Salt',
                'NUTRIENT_CONTENT_CLAIM',
                'both',
                'ALL',
                NULL,
                NULL,
                NULL,
                '{"logical_operator": "AND", "conditions": [{"type": "NUTRIENT_THRESHOLD", "nutrient_code": "sodium", "operator": "LTE", "threshold_value": 120.0, "measurement_basis": "PER_100G", "food_form": "both"}]}'::jsonb,
                '["Low in Sodium", "Low Salt", "Little Salt"]'::jsonb,
                'FSSAI (Advertising and Claims) Regulations 2018, Schedule I, Entry 7(b)',
                'Version III (04-10-2022)',
                '2019-07-01'::date,
                TRUE,
                'Contains sodium not exceeding 120mg per 100g (equivalent to 0.3g salt per 100g).'
            ) ON CONFLICT (claim_id) DO NOTHING
            RETURNING claim_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'regulatory_claim_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                'ir_aspartame_pku_warning',
                'ins_951_aspartame',
                'MANDATORY_LABEL_WARNING',
                'ALL',
                NULL,
                'CONTAINS ASPARTAME. NOT RECOMMENDED FOR PHENYLKETONURICS.',
                NULL,
                'FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 1',
                'Aspartame metabolizes into phenylalanine. Phenylketonurics (individuals with PKU) must avoid.'
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredient_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                'ir_maltitol_laxative_warning',
                'ins_965_maltitol',
                'MANDATORY_LABEL_WARNING',
                'ALL',
                NULL,
                'Polyols may produce laxative effects.',
                NULL,
                'FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 4',
                'Polyol sweeteners may cause gastrointestinal discomfort or laxative effects when consumed in large quantities.'
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredient_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                'ir_sorbitol_laxative_warning',
                'ins_420_sorbitol',
                'MANDATORY_LABEL_WARNING',
                'ALL',
                NULL,
                'Polyols may produce laxative effects.',
                NULL,
                'FSSAI (Labelling and Display) Regulations 2020, Schedule II, Entry 4',
                'Polyol sweeteners may cause gastrointestinal discomfort or laxative effects.'
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredient_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                'ir_caffeine_warning',
                'caffeine',
                'MANDATORY_LABEL_WARNING',
                'BEVERAGE',
                300.0,
                'CONTAINS CAFFEINE. Not recommended for children, pregnant or lactating women.',
                NULL,
                'FSSAI (Food Products Standards and Food Additives) Regulations 2011, Appendix A Table 3',
                'Caffeine in energy drinks / caffeinated beverages requires prominent population advisory.'
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredient_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                'ir_sodium_benzoate_max_limit_beverages',
                'ins_211_sodium_benzoate',
                'MAX_PERMISSIBLE_LIMIT',
                'BEVERAGE',
                120.0,
                NULL,
                NULL,
                'FSSAI (Food Products Standards and Food Additives) Regulations 2011, Appendix A Table 3',
                'Preservative limited to a maximum of 120 ppm in water-based flavoured drinks.'
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredient_rules', pk FROM ins;;

WITH ins AS (
            INSERT INTO ingredient_rules (
                rule_id, ingredient_code, rule_type, target_food_category,
                max_permitted_ppm, warning_statement, condition_expression,
                regulatory_reference, consumer_guidance
            ) VALUES (
                'ir_potassium_sorbate_max_limit_confectionery',
                'ins_202_potassium_sorbate',
                'MAX_PERMISSIBLE_LIMIT',
                'CONFECTIONERY',
                1000.0,
                NULL,
                NULL,
                'FSSAI (Food Products Standards and Food Additives) Regulations 2011, Appendix A Table 3',
                'Sorbate preservative limited to 1,000 ppm in flour confectionery and frostings.'
            ) ON CONFLICT (rule_id) DO NOTHING
            RETURNING rule_id AS pk
        )
        INSERT INTO migration_seed_ownership (migration_revision, target_table, record_id)
        SELECT '0003_seed_verified_rule_data', 'ingredient_rules', pk FROM ins;;

UPDATE alembic_version SET version_num='0003_seed_verified_rule_data' WHERE alembic_version.version_num = '0002_enhance_rules';

COMMIT;

