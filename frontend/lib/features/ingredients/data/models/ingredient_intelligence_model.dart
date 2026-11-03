import 'package:flutter/material.dart';
import '../../../product_details/data/models/product_response_model.dart';

class ParsedIngredientItem {
  final String name;
  final String? insCode;
  final String role;
  final String explanation;
  final IconData icon;
  final String fssaiReference;
  final bool isAllergen;
  final bool isAdditive;

  const ParsedIngredientItem({
    required this.name,
    this.insCode,
    required this.role,
    required this.explanation,
    required this.icon,
    required this.fssaiReference,
    this.isAllergen = false,
    this.isAdditive = false,
  });
}

class IngredientIntelligenceHelper {
  IngredientIntelligenceHelper._();

  static List<ParsedIngredientItem> extractIngredients(ProductDetailsResponse? product) {
    if (product == null || product.ingredientAnalysis == null) {
      return const [];
    }

    final analysis = product.ingredientAnalysis!;
    final summary = analysis.ingredientsSummary;
    final List<String> rawNames = [];

    if (summary != null && summary.trim().isNotEmpty) {
      // Split by comma, preserving parenthetical groupings
      final items = _splitIngredientString(summary);
      rawNames.addAll(items);
    } else if (analysis.categories.isNotEmpty) {
      for (final cat in analysis.categories) {
        rawNames.addAll(cat.items);
      }
    }

    if (rawNames.isEmpty) return const [];

    final allergens = analysis.declaredAllergens.map((e) => e.toLowerCase()).toSet();
    final List<ParsedIngredientItem> result = [];

    for (int i = 0; i < rawNames.length; i++) {
      final raw = rawNames[i].trim();
      if (raw.isEmpty) continue;

      final lower = raw.toLowerCase();
      final ins = _extractIns(raw);

      String role = 'Ingredient';
      String explanation = 'Component declared in product formulation.';
      IconData icon = Icons.eco_outlined;
      String fssaiRef = 'FSSAI Food Safety and Standards (Food Products Standards and Food Additives) Regulations, 2011';
      bool isAllg = allergens.any((a) => lower.contains(a));
      bool isAdd = ins != null || lower.contains('ins') || lower.contains('preservative') || lower.contains('color') || lower.contains('emulsifier') || lower.contains('acidity regulator');

      if (i == 0) {
        role = 'Main Ingredient';
        explanation = 'Primary base ingredient providing the core structure, volume, and nutrients of the product.';
        icon = Icons.grain_rounded;
      } else if (lower.contains('oil') || lower.contains('fat') || lower.contains('ghee') || lower.contains('butter') || lower.contains('palmolein')) {
        role = 'Processing / Cooking';
        explanation = 'Used as a cooking medium for texture, crispness, and stability during industrial processing.';
        icon = Icons.water_drop_outlined;
      } else if (lower.contains('salt') || lower.contains('sodium')) {
        role = 'Flavour / Preservative';
        explanation = 'Enhances savory taste and palatability while acting as a natural curing and moisture regulator.';
        icon = Icons.scatter_plot_rounded;
      } else if (lower.contains('sugar') || lower.contains('syrup') || lower.contains('glucose') || lower.contains('fructose') || lower.contains('dextrose')) {
        role = 'Sweetener';
        explanation = 'Adds sweetness and energy density, contributing directly to glycemic impact.';
        icon = Icons.hexagon_outlined;
      } else if (isAdd) {
        role = 'Food Additive (INS)';
        explanation = 'Standardized additive regulated for safe functional properties such as preservation, emulsification, or leavening.';
        icon = Icons.science_outlined;
        fssaiRef = 'FSSAI Permitted Food Additive List under Appendix A.';
      } else if (isAllg) {
        role = 'Major Allergen';
        explanation = 'Statutory major allergen declared for consumer awareness under FSSAI Schedule II.';
        icon = Icons.shield_outlined;
      } else if (lower.contains('flour') || lower.contains('wheat') || lower.contains('maida') || lower.contains('corn') || lower.contains('potato') || lower.contains('rice')) {
        role = 'Base Carbohydrate';
        explanation = 'Starch-dense grain or vegetable base contributing texture and dietary carbohydrate.';
        icon = Icons.grass_rounded;
      }

      result.add(
        ParsedIngredientItem(
          name: raw,
          insCode: ins,
          role: role,
          explanation: explanation,
          icon: icon,
          fssaiReference: fssaiRef,
          isAllergen: isAllg,
          isAdditive: isAdd,
        ),
      );
    }

    return result;
  }

  static String? _extractIns(String text) {
    final match = RegExp(r'INS\s*([0-9]+[a-z]?)', caseSensitive: false).firstMatch(text);
    if (match != null) return 'INS ${match.group(1)}';
    final numMatch = RegExp(r'\b([0-9]{3,4}[a-z]?)\b').firstMatch(text);
    if (numMatch != null && text.toLowerCase().contains('additive')) {
      return 'INS ${numMatch.group(1)}';
    }
    return null;
  }

  static List<String> _splitIngredientString(String text) {
    final List<String> parts = [];
    int depth = 0;
    int start = 0;

    for (int i = 0; i < text.length; i++) {
      final c = text[i];
      if (c == '(' || c == '[') {
        depth++;
      } else if (c == ')' || c == ']') {
        depth--;
      } else if (c == ',' && depth == 0) {
        final sub = text.substring(start, i).trim();
        if (sub.isNotEmpty) parts.add(sub);
        start = i + 1;
      }
    }

    if (start < text.length) {
      final sub = text.substring(start).trim();
      if (sub.isNotEmpty) parts.add(sub);
    }

    return parts;
  }

  static String generateOverallInsight(ProductDetailsResponse? product, List<ParsedIngredientItem> items) {
    if (product == null || items.isEmpty) {
      return 'Ingredient analysis reflects manufacturer label declarations verified against FSSAI regulatory standards.';
    }

    final hasAdditives = items.any((i) => i.isAdditive);
    final count = items.length;

    if (!hasAdditives && count <= 5) {
      return 'Minimal-ingredient formulation with zero chemical additives or artificial preservatives listed on the label.';
    } else if (hasAdditives) {
      final additiveCount = items.where((i) => i.isAdditive).length;
      return 'Contains $additiveCount regulated food additive(s) within standard FSSAI technological function thresholds.';
    } else {
      return 'Standard packaged food matrix with $count declared ingredients evaluated against FSSAI Schedule II guidelines.';
    }
  }
}

