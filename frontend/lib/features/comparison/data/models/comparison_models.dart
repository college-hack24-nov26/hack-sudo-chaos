import 'package:flutter/material.dart';
import '../../../product_details/data/models/product_response_model.dart';

class ComparisonNutrientRow {
  final String key;
  final String displayName;
  final IconData icon;
  final String unit;
  final double? valueA;
  final double? valueB;
  final double progressA; // 0.0 to 1.0
  final double progressB; // 0.0 to 1.0
  final Color colorA;
  final Color colorB;

  const ComparisonNutrientRow({
    required this.key,
    required this.displayName,
    required this.icon,
    required this.unit,
    this.valueA,
    this.valueB,
    required this.progressA,
    required this.progressB,
    required this.colorA,
    required this.colorB,
  });

  String get formattedValueA {
    if (valueA == null) return 'N/A';
    final rounded = valueA!.toStringAsFixed(valueA!.truncateToDouble() == valueA! ? 0 : 1);
    return '$rounded $unit';
  }

  String get formattedValueB {
    if (valueB == null) return 'N/A';
    final rounded = valueB!.toStringAsFixed(valueB!.truncateToDouble() == valueB! ? 0 : 1);
    return '$rounded $unit';
  }
}

class ComparisonTakeaway {
  final IconData icon;
  final Color iconColor;
  final Color? iconBgColor;
  final String boldSubject;
  final String text;

  const ComparisonTakeaway({
    required this.icon,
    required this.iconColor,
    this.iconBgColor,
    required this.boldSubject,
    required this.text,
  });
}

class ComparisonAnalysisHelper {
  ComparisonAnalysisHelper._();

  static List<ComparisonNutrientRow> computeNutrientRows({
    required ProductDetailsResponse? productA,
    required ProductDetailsResponse? productB,
  }) {
    const defs = [
      _NutrientDef(
        key: 'energy',
        displayName: 'Energy',
        icon: Icons.bolt_rounded,
        defaultUnit: 'kcal',
        codes: ['energy', 'energy_kcal', 'calories', 'calorie'],
        maxScale: 600.0,
        isLowerBetter: true,
      ),
      _NutrientDef(
        key: 'carbohydrates',
        displayName: 'Carbohydrates',
        icon: Icons.grain_rounded,
        defaultUnit: 'g',
        codes: ['carbohydrates', 'carbohydrate', 'total_carbs', 'carbs'],
        maxScale: 100.0,
        isLowerBetter: null,
      ),
      _NutrientDef(
        key: 'total_fat',
        displayName: 'Total Fat',
        icon: Icons.water_drop_outlined,
        defaultUnit: 'g',
        codes: ['fat', 'total_fat', 'lipids'],
        maxScale: 40.0,
        isLowerBetter: true,
      ),
      _NutrientDef(
        key: 'sugar',
        displayName: 'Sugar',
        icon: Icons.hexagon_outlined,
        defaultUnit: 'g',
        codes: ['sugars', 'sugar', 'added_sugars', 'total_sugars'],
        maxScale: 35.0,
        isLowerBetter: true,
      ),
      _NutrientDef(
        key: 'protein',
        displayName: 'Protein',
        icon: Icons.fitness_center_rounded,
        defaultUnit: 'g',
        codes: ['protein', 'proteins'],
        maxScale: 30.0,
        isLowerBetter: false, // higher is better
      ),
      _NutrientDef(
        key: 'sodium',
        displayName: 'Sodium',
        icon: Icons.scatter_plot_rounded,
        defaultUnit: 'mg',
        codes: ['sodium', 'salt', 'na'],
        maxScale: 1500.0,
        isLowerBetter: true,
      ),
    ];

    return defs.map((def) {
      final itemA = _findNutrient(productA, def.codes);
      final itemB = _findNutrient(productB, def.codes);

      final valA = itemA?.valuePer100g;
      final valB = itemB?.valuePer100g;
      final unit = itemA?.unit ?? itemB?.unit ?? def.defaultUnit;

      final progA = valA == null ? 0.0 : (valA / def.maxScale).clamp(0.04, 1.0);
      final progB = valB == null ? 0.0 : (valB / def.maxScale).clamp(0.04, 1.0);

      final colorA = _determineBarColor(valA, valB, def.isLowerBetter, itemA?.concernLevel);
      final colorB = _determineBarColor(valB, valA, def.isLowerBetter, itemB?.concernLevel);

      return ComparisonNutrientRow(
        key: def.key,
        displayName: def.displayName,
        icon: def.icon,
        unit: unit,
        valueA: valA,
        valueB: valB,
        progressA: progA,
        progressB: progB,
        colorA: colorA,
        colorB: colorB,
      );
    }).toList();
  }

  static Color _determineBarColor(
    double? myVal,
    double? otherVal,
    bool? isLowerBetter,
    String? concernLevel,
  ) {
    if (myVal == null) return const Color(0xFFD4CFCB); // Empty grey

    if (concernLevel == 'CONCERN') return const Color(0xFFF0485E); // Red
    if (concernLevel == 'POSITIVE') return const Color(0xFF52B76A); // Green
    if (concernLevel == 'NEUTRAL') return const Color(0xFFF4A636); // Amber

    if (otherVal != null && isLowerBetter != null) {
      if (isLowerBetter) {
        if (myVal > otherVal * 1.15) return const Color(0xFFF0485E); // Higher bad -> red
        if (myVal < otherVal * 0.85) return const Color(0xFF52B76A); // Lower bad -> green
        return const Color(0xFFF4A636); // Amber
      } else {
        // Higher is better (e.g. protein)
        if (myVal > otherVal * 1.15) return const Color(0xFF52B76A); // Higher good -> green
        if (myVal < otherVal * 0.85) return const Color(0xFFF4A636); // Lower good -> amber
        return const Color(0xFF52B76A);
      }
    }

    return const Color(0xFFF4A636);
  }

  static NutrientItem? _findNutrient(ProductDetailsResponse? product, List<String> codes) {
    if (product == null || product.nutritionalInterpretation == null) return null;
    final nutrients = product.nutritionalInterpretation!.nutrients;
    for (final code in codes) {
      final match = nutrients.where(
        (n) => n.nutrientCode.toLowerCase() == code || n.displayName.toLowerCase().contains(code),
      );
      if (match.isNotEmpty) return match.first;
    }
    return null;
  }

  static List<ComparisonTakeaway> computeTakeaways({
    required ProductDetailsResponse? productA,
    required ProductDetailsResponse? productB,
  }) {
    if (productA == null || productB == null) {
      return const [
        ComparisonTakeaway(
          icon: Icons.info_rounded,
          iconColor: Color(0xFF4A3B69),
          iconBgColor: Color(0xFFD9CBF2),
          boldSubject: 'Select two products',
          text: ' to generate automated ICMR-NIN nutritional differences and ingredient intelligence.',
        ),
      ];
    }

    final takeaways = <ComparisonTakeaway>[];
    final nameA = productA.product.productName;
    final nameB = productB.product.productName;

    // Check Sugar
    final sugarA = _findNutrient(productA, ['sugars', 'sugar'])?.valuePer100g;
    final sugarB = _findNutrient(productB, ['sugars', 'sugar'])?.valuePer100g;
    if (sugarA != null && sugarB != null && (sugarA - sugarB).abs() >= 1.0) {
      final higherProd = sugarA > sugarB ? nameA : nameB;
      final diff = (sugarA - sugarB).abs().toStringAsFixed(1);
      takeaways.add(
        ComparisonTakeaway(
          icon: Icons.warning_amber_rounded,
          iconColor: const Color(0xFFF4A636),
          boldSubject: higherProd,
          text: ' contains $diff g more sugar per 100 g, which may impact glycemic response.',
        ),
      );
    }

    // Check Protein
    final proteinA = _findNutrient(productA, ['protein', 'proteins'])?.valuePer100g;
    final proteinB = _findNutrient(productB, ['protein', 'proteins'])?.valuePer100g;
    if (proteinA != null && proteinB != null && (proteinA - proteinB).abs() >= 0.8) {
      final higherProd = proteinA > proteinB ? nameA : nameB;
      final diff = (proteinA - proteinB).abs().toStringAsFixed(1);
      takeaways.add(
        ComparisonTakeaway(
          icon: Icons.check_circle_rounded,
          iconColor: const Color(0xFF4BB565),
          boldSubject: higherProd,
          text: ' offers $diff g higher protein per 100 g, providing better satiety and nutritional value.',
        ),
      );
    }

    // Check Sodium
    final sodiumA = _findNutrient(productA, ['sodium', 'salt'])?.valuePer100g;
    final sodiumB = _findNutrient(productB, ['sodium', 'salt'])?.valuePer100g;
    if (sodiumA != null && sodiumB != null && (sodiumA - sodiumB).abs() >= 50.0) {
      final lowerProd = sodiumA < sodiumB ? nameA : nameB;
      final diff = (sodiumA - sodiumB).abs().toStringAsFixed(0);
      takeaways.add(
        ComparisonTakeaway(
          icon: Icons.check_circle_rounded,
          iconColor: const Color(0xFF4BB565),
          boldSubject: lowerProd,
          text: ' has $diff mg lower sodium, making it a safer option for cardiovascular health.',
        ),
      );
    }

    // Fallback or summary takeaway
    if (takeaways.isEmpty) {
      takeaways.add(
        const ComparisonTakeaway(
          icon: Icons.info_rounded,
          iconColor: Color(0xFF4A3B69),
          iconBgColor: Color(0xFFD9CBF2),
          boldSubject: 'Comparable Nutritional Profile:',
          text: ' Both products show balanced macronutrient ranges based on declared standard values.',
        ),
      );
    }

    // Data completeness / provenance note
    final incompleteA = productA.nutritionalInterpretation == null || productA.nutritionalInterpretation!.nutrients.isEmpty;
    final incompleteB = productB.nutritionalInterpretation == null || productB.nutritionalInterpretation!.nutrients.isEmpty;
    if (incompleteA || incompleteB) {
      takeaways.add(
        const ComparisonTakeaway(
          icon: Icons.info_rounded,
          iconColor: Color(0xFF4A3B69),
          iconBgColor: Color(0xFFD9CBF2),
          boldSubject: 'Data Notice:',
          text: ' One or more products have undeclared nutrient fields. Comparison reflects only verified manufacturer values.',
        ),
      );
    }

    return takeaways;
  }

  static String computeYourChoiceSummary({
    required ProductDetailsResponse? productA,
    required ProductDetailsResponse? productB,
  }) {
    if (productA == null || productB == null) {
      return 'Select two foods to generate an evidence-based comparison and smart choice recommendation.';
    }

    final nameA = productA.product.productName;
    final nameB = productB.product.productName;

    final sugarA = _findNutrient(productA, ['sugars', 'sugar'])?.valuePer100g ?? 0.0;
    final sugarB = _findNutrient(productB, ['sugars', 'sugar'])?.valuePer100g ?? 0.0;
    final proteinA = _findNutrient(productA, ['protein', 'proteins'])?.valuePer100g ?? 0.0;
    final proteinB = _findNutrient(productB, ['protein', 'proteins'])?.valuePer100g ?? 0.0;

    int scoreA = 0;
    int scoreB = 0;

    if (sugarA < sugarB) {
      scoreA++;
    } else if (sugarB < sugarA) {
      scoreB++;
    }

    if (proteinA > proteinB) {
      scoreA++;
    } else if (proteinB > proteinA) {
      scoreB++;
    }

    if (scoreA > scoreB) {
      return '$nameA appears to be the more balanced choice, offering lower sugar and favorable nutrient density.';
    } else if (scoreB > scoreA) {
      return '$nameB appears to be the more balanced choice, offering lower sugar and favorable nutrient density.';
    } else {
      return 'Both products offer distinct nutritional trade-offs. Review the specific macronutrient targets for your dietary needs.';
    }
  }

  static String extractIngredientsGlance(ProductDetailsResponse? product) {
    if (product == null || product.ingredientAnalysis == null) {
      return 'Not declared';
    }
    final summary = product.ingredientAnalysis!.ingredientsSummary;
    if (summary != null && summary.trim().isNotEmpty) {
      // Return first 2-3 items
      final parts = summary.split(',').map((s) => s.trim()).take(3).toList();
      return parts.join(', ');
    }
    final total = product.ingredientAnalysis!.totalIngredientsCount;
    if (total > 0) return '$total ingredients declared';
    return 'Not declared';
  }

  static String extractAllergenGlance(ProductDetailsResponse? product) {
    if (product == null || product.ingredientAnalysis == null) {
      return 'Not specified';
    }
    final allergens = product.ingredientAnalysis!.declaredAllergens;
    if (allergens.isNotEmpty) {
      return allergens.take(2).join(', ');
    }
    final mayContain = product.ingredientAnalysis!.mayContainAllergens;
    if (mayContain.isNotEmpty) {
      return 'May contain ${mayContain.take(2).join(", ")}';
    }
    return 'None declared';
  }
}

class _NutrientDef {
  final String key;
  final String displayName;
  final IconData icon;
  final String defaultUnit;
  final List<String> codes;
  final double maxScale;
  final bool? isLowerBetter;

  const _NutrientDef({
    required this.key,
    required this.displayName,
    required this.icon,
    required this.defaultUnit,
    required this.codes,
    required this.maxScale,
    required this.isLowerBetter,
  });
}
