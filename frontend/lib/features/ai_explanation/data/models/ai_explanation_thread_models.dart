import 'package:flutter/material.dart';
import '../../../product_details/data/models/product_response_model.dart';

enum AiReasonSeverity { high, moderate, info, positive }

class AiKeyReason {
  final String label;
  final AiReasonSeverity severity;
  final IconData icon;
  final String? valueText;
  final String explanation;

  const AiKeyReason({
    required this.label,
    required this.severity,
    required this.icon,
    this.valueText,
    required this.explanation,
  });

  Color get pillBackgroundColor {
    switch (severity) {
      case AiReasonSeverity.high:
        return const Color(0xFFFDE8E8);
      case AiReasonSeverity.moderate:
        return const Color(0xFFFBF0DC);
      case AiReasonSeverity.info:
        return const Color(0xFFECE4FA);
      case AiReasonSeverity.positive:
        return const Color(0xFFE3F5E8);
    }
  }

  Color get pillTextColor {
    switch (severity) {
      case AiReasonSeverity.high:
        return const Color(0xFFB82828);
      case AiReasonSeverity.moderate:
        return const Color(0xFF7A4F1D);
      case AiReasonSeverity.info:
        return const Color(0xFF5E3DC4);
      case AiReasonSeverity.positive:
        return const Color(0xFF1E6F32);
    }
  }
}

class AiStructuredResponse {
  final String boldConclusion;
  final String bodyText;
  final List<AiKeyReason> keyReasons;
  final String inShort;

  const AiStructuredResponse({
    required this.boldConclusion,
    required this.bodyText,
    required this.keyReasons,
    required this.inShort,
  });
}

class AiChatMessage {
  final String id;
  final String question;
  final AiStructuredResponse? response;
  final bool isLoading;
  final String? errorMessage;
  final DateTime timestamp;

  const AiChatMessage({
    required this.id,
    required this.question,
    this.response,
    this.isLoading = false,
    this.errorMessage,
    required this.timestamp,
  });
}

class AiExplanationEngine {
  AiExplanationEngine._();

  static AiStructuredResponse generateResponse({
    required String question,
    required ProductDetailsResponse? product,
  }) {
    final q = question.toLowerCase();

    final name = product?.product.productName ?? 'This product';
    final nutrients = product?.nutritionalInterpretation?.nutrients ?? [];

    double? findVal(List<String> codes) {
      for (final n in nutrients) {
        final c = n.nutrientCode.toLowerCase();
        final d = n.displayName.toLowerCase();
        if (codes.any((code) => c == code || d.contains(code))) {
          return n.valuePer100g;
        }
      }
      return null;
    }

    final fatVal = findVal(['fat', 'total_fat']);
    final sugarVal = findVal(['sugar', 'sugars', 'added_sugars']);
    final sodiumVal = findVal(['sodium', 'salt']);
    final energyVal = findVal(['energy', 'energy_kcal', 'calories']);
    final proteinVal = findVal(['protein', 'proteins']);

    final hasAdditives = product?.ingredientAnalysis?.categories.any((c) => c.category == 'ADDITIVES') ?? false;
    final totalAdditives = product?.ingredientAnalysis?.categories
            .firstWhere((c) => c.category == 'ADDITIVES', orElse: () => const IngredientCategory(category: '', categoryName: '', count: 0, items: []))
            .count ??
        0;

    // 1. Daily consumption
    if (q.contains('daily') || q.contains('every day') || q.contains('routine')) {
      final isHighInSomething = (fatVal != null && fatVal > 20.0) || (sugarVal != null && sugarVal > 15.0) || (sodiumVal != null && sodiumVal > 500.0);

      final reasons = <AiKeyReason>[];
      if (fatVal != null) {
        reasons.add(
          AiKeyReason(
            label: 'Total Fat',
            severity: fatVal > 20.0 ? AiReasonSeverity.high : AiReasonSeverity.moderate,
            icon: Icons.water_drop_outlined,
            valueText: '${fatVal.toStringAsFixed(1)} g',
            explanation: 'High fat density makes it calorie-heavy and slower to metabolize.',
          ),
        );
      }
      if (sodiumVal != null) {
        reasons.add(
          AiKeyReason(
            label: 'Sodium',
            severity: sodiumVal > 500.0 ? AiReasonSeverity.high : AiReasonSeverity.moderate,
            icon: Icons.scatter_plot_rounded,
            valueText: '${sodiumVal.toStringAsFixed(0)} mg',
            explanation: 'Contributes a notable share of your 2,000 mg recommended daily sodium ceiling.',
          ),
        );
      }
      if (energyVal != null) {
        reasons.add(
          AiKeyReason(
            label: 'Energy',
            severity: energyVal > 400.0 ? AiReasonSeverity.info : AiReasonSeverity.moderate,
            icon: Icons.bolt_rounded,
            valueText: '${energyVal.toStringAsFixed(0)} kcal',
            explanation: 'High energy density per 100 g portion can lead to unintentional calorie surplus.',
          ),
        );
      }

      if (isHighInSomething) {
        return AiStructuredResponse(
          boldConclusion: 'Not recommended for daily consumption.',
          bodyText:
              ' Because of elevated levels of saturated fats, sodium, or energy density, consuming this regularly may impact dietary balance over time.',
          keyReasons: reasons,
          inShort: 'Enjoy occasionally as a treat rather than as an everyday dietary staple.',
        );
      } else {
        return AiStructuredResponse(
          boldConclusion: 'Acceptable in moderation.',
          bodyText:
              ' This product presents a balanced macronutrient composition within standard Indian RDA recommendations.',
          keyReasons: reasons,
          inShort: 'Can fit into a well-rounded diet with proper portion mindfulness.',
        );
      }
    }

    // 2. Sodium / Salt question
    if (q.contains('sodium') || q.contains('salt')) {
      final sValStr = sodiumVal != null ? '${sodiumVal.toStringAsFixed(0)} mg' : 'Declared level';
      return AiStructuredResponse(
        boldConclusion: 'Sodium is elevated for flavor and shelf-stability.',
        bodyText:
            ' In packaged foods, salt enhances sensory appeal and crispness while serving preservation functions.',
        keyReasons: [
          AiKeyReason(
            label: 'Sodium Content',
            severity: (sodiumVal ?? 0) > 500 ? AiReasonSeverity.high : AiReasonSeverity.moderate,
            icon: Icons.scatter_plot_rounded,
            valueText: sValStr,
            explanation: 'Represents verified manufacturer label declarations per 100 g.',
          ),
          const AiKeyReason(
            label: 'Preservation',
            severity: AiReasonSeverity.moderate,
            icon: Icons.shield_outlined,
            explanation: 'Sodium helps maintain moisture barrier and microbiological stability.',
          ),
        ],
        inShort: 'Be mindful of portion size if tracking daily cardiovascular salt limits.',
      );
    }

    // 3. Additives / Chemicals question
    if (q.contains('additive') || q.contains('harmful') || q.contains('chemical') || q.contains('ins')) {
      if (!hasAdditives || totalAdditives == 0) {
        return const AiStructuredResponse(
          boldConclusion: 'No chemical additives or artificial preservatives listed.',
          bodyText:
              ' The packaging reflects simple, declared food ingredients without standard INS functional food additive codes.',
          keyReasons: [
            AiKeyReason(
              label: 'Zero Additives',
              severity: AiReasonSeverity.positive,
              icon: Icons.eco_outlined,
              explanation: 'No synthetic flavor enhancers or artificial preservatives declared.',
            ),
          ],
          inShort: 'Formulation relies on traditional cooking mediums without added chemical stabilizers.',
        );
      } else {
        return AiStructuredResponse(
          boldConclusion: 'Contains approved technological additives.',
          bodyText:
              ' Contains $totalAdditives food additive(s) evaluated under FSSAI Food Additive regulations for safe consumption thresholds.',
          keyReasons: [
            AiKeyReason(
              label: 'Permitted INS',
              severity: AiReasonSeverity.info,
              icon: Icons.science_outlined,
              valueText: '$totalAdditives items',
              explanation: 'Additives used comply with statutory limits for texture and freshness.',
            ),
          ],
          inShort: 'All declared additives are within statutory safety parameters.',
        );
      }
    }

    // 4. Healthier / Snack option question
    if (q.contains('healthier') || q.contains('snack') || q.contains('alternative')) {
      final isHighSugar = (sugarVal ?? 0) > 10.0;
      final isHighFat = (fatVal ?? 0) > 20.0;

      return AiStructuredResponse(
        boldConclusion: isHighSugar || isHighFat ? 'It is an indulgent snack option.' : 'Provides moderate nutritional value.',
        bodyText:
            ' Compared to whole foods like roasted nuts, boiled pulses, or fresh fruit, packaged snacks typically feature lower micronutrient density.',
        keyReasons: [
          if (fatVal != null)
            AiKeyReason(
              label: 'Fat Ratio',
              severity: isHighFat ? AiReasonSeverity.high : AiReasonSeverity.moderate,
              icon: Icons.water_drop_outlined,
              valueText: '${fatVal.toStringAsFixed(1)} g',
              explanation: 'Accounts for a substantial portion of overall calorie contribution.',
            ),
          if (proteinVal != null)
            AiKeyReason(
              label: 'Protein',
              severity: proteinVal > 5.0 ? AiReasonSeverity.positive : AiReasonSeverity.moderate,
              icon: Icons.fitness_center_rounded,
              valueText: '${proteinVal.toStringAsFixed(1)} g',
              explanation: 'Provides dietary protein contributing toward satiety.',
            ),
        ],
        inShort: 'Pair with raw veggies, yogurt, or high-fiber foods to balance nutrient intake.',
      );
    }

    // 5. Default / General inquiry
    final lead = product?.aiExplanation?.text ?? '$name nutritional analysis evaluated under ICMR-NIN guidelines.';
    return AiStructuredResponse(
      boldConclusion: 'Nutritional overview and dietary assessment.',
      bodyText: ' $lead',
      keyReasons: [
        if (fatVal != null)
          AiKeyReason(
            label: 'Fat',
            severity: fatVal > 20 ? AiReasonSeverity.high : AiReasonSeverity.moderate,
            icon: Icons.water_drop_outlined,
            valueText: '${fatVal.toStringAsFixed(1)} g',
            explanation: 'Declared total fat per 100 g standard measurement.',
          ),
        if (sodiumVal != null)
          AiKeyReason(
            label: 'Sodium',
            severity: sodiumVal > 500 ? AiReasonSeverity.high : AiReasonSeverity.moderate,
            icon: Icons.scatter_plot_rounded,
            valueText: '${sodiumVal.toStringAsFixed(0)} mg',
            explanation: 'Declared sodium per 100 g portion.',
          ),
      ],
      inShort: 'Always consult the full nutritional panel for personalized dietary requirements.',
    );
  }

  static AiStructuredResponse fromBackendAnswer({
    required String answer,
    required ProductDetailsResponse? product,
    required String question,
  }) {
    final fallback = generateResponse(question: question, product: product);
    final firstSentence = answer.contains('.') ? '${answer.split('.').first.trim()}.' : answer;
    return AiStructuredResponse(
      boldConclusion: firstSentence,
      bodyText: answer,
      keyReasons: fallback.keyReasons,
      inShort: answer.length > 120 ? '${answer.substring(0, 120).trim()}...' : answer,
    );
  }
}
