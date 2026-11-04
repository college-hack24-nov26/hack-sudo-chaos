import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class NutrientRowCard extends StatelessWidget {
  final NutrientItem nutrient;
  final bool isPerServing;
  final bool isExpanded;
  final VoidCallback onToggleExpand;

  const NutrientRowCard({
    super.key,
    required this.nutrient,
    required this.isPerServing,
    required this.isExpanded,
    required this.onToggleExpand,
  });

  IconData _getNutrientIcon() {
    switch (nutrient.nutrientCode.toLowerCase()) {
      case 'carbohydrates':
      case 'carbs':
        return Icons.grain_rounded;
      case 'sugars':
      case 'sugar':
      case 'total_sugars':
      case 'added_sugars':
        return Icons.view_in_ar_rounded;
      case 'total_fat':
      case 'fat':
      case 'saturated_fat':
        return Icons.water_drop_rounded;
      case 'protein':
      case 'proteins':
        return Icons.fitness_center_rounded;
      case 'sodium':
      case 'salt':
        return Icons.egg_rounded;
      case 'dietary_fibre':
      case 'fibre':
        return Icons.spa_rounded;
      default:
        return Icons.scatter_plot_rounded;
    }
  }

  Color _getIconColor() {
    switch (nutrient.nutrientCode.toLowerCase()) {
      case 'carbohydrates':
        return AppColors.nutrientCarbs;
      case 'sugars':
      case 'total_sugars':
      case 'added_sugars':
        return AppColors.nutrientSugar;
      case 'total_fat':
      case 'fat':
      case 'saturated_fat':
        return AppColors.nutrientFat;
      case 'protein':
        return AppColors.nutrientProtein;
      case 'sodium':
      case 'salt':
        return AppColors.nutrientSodium;
      default:
        return AppColors.neutral;
    }
  }

  Color _getIconBgColor() {
    switch (nutrient.nutrientCode.toLowerCase()) {
      case 'carbohydrates':
        return AppColors.nutrientCarbsBg;
      case 'sugars':
      case 'total_sugars':
      case 'added_sugars':
        return AppColors.nutrientSugarBg;
      case 'total_fat':
      case 'fat':
      case 'saturated_fat':
        return AppColors.nutrientFatBg;
      case 'protein':
        return AppColors.nutrientProteinBg;
      case 'sodium':
      case 'salt':
        return AppColors.nutrientSodiumBg;
      default:
        return AppColors.neutralBackground;
    }
  }

  @override
  Widget build(BuildContext context) {
    final displayValue = isPerServing
        ? nutrient.valuePerServing
        : nutrient.valuePer100g;

    final formattedValue = displayValue != null
        ? '${displayValue.toStringAsFixed(displayValue.truncateToDouble() == displayValue ? 0 : 1)} ${nutrient.unit}'
        : '—';

    final hasThresholds = nutrient.hasThresholdScale && displayValue != null;

    return Container(
      margin: const EdgeInsets.only(bottom: AppSpacing.sm),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onToggleExpand,
          borderRadius: AppSpacing.borderRadiusCard,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Main Header Row
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    // Nutrient Icon
                    Container(
                      width: 36.0,
                      height: 36.0,
                      decoration: BoxDecoration(
                        color: _getIconBgColor(),
                        shape: BoxShape.circle,
                      ),
                      alignment: Alignment.center,
                      child: Icon(_getNutrientIcon(), size: 18.0, color: _getIconColor()),
                    ),
                    const SizedBox(width: AppSpacing.md),
                    // Name & Value
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(nutrient.displayName, style: AppTypography.h3),
                              Text(formattedValue, style: AppTypography.valueMedium),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: AppSpacing.sm),
                    // Classification Badge (Backend provided)
                    if (nutrient.classification != null) ...[
                      _ClassificationBadge(classification: nutrient.classification!),
                      const SizedBox(width: 4.0),
                    ],
                    Icon(
                      isExpanded ? Icons.keyboard_arrow_up_rounded : Icons.keyboard_arrow_down_rounded,
                      size: 20.0,
                      color: AppColors.textTertiary,
                    ),
                  ],
                ),

                // Threshold Visual Scale (Scaled to match current basis so visual marker matches classification)
                if (hasThresholds) ...[
                  const SizedBox(height: 10.0),
                  Padding(
                    padding: const EdgeInsets.only(left: 48.0),
                    child: Builder(
                      builder: (context) {
                        double scaleFactor = 1.0;
                        if (isPerServing &&
                            nutrient.valuePerServing != null &&
                            nutrient.valuePer100g != null &&
                            nutrient.valuePer100g! > 0) {
                          scaleFactor = nutrient.valuePerServing! / nutrient.valuePer100g!;
                        }
                        return _ThresholdScaleBar(
                          value: displayValue,
                          lowMax: nutrient.lowThresholdMax! * scaleFactor,
                          moderateMax: nutrient.moderateThresholdMax! * scaleFactor,
                          highMin: nutrient.highThresholdMin! * scaleFactor,
                        );
                      },
                    ),
                  ),
                ],

                // Explanation text
                if (nutrient.explanation != null && nutrient.explanation!.isNotEmpty) ...[
                  const SizedBox(height: 8.0),
                  Padding(
                    padding: const EdgeInsets.only(left: 48.0),
                    child: Text(
                      nutrient.explanation!,
                      style: AppTypography.bodySmall,
                    ),
                  ),
                ],

                // Expanded Section: RDA & Clinical reference values
                if (isExpanded) ...[
                  const SizedBox(height: 12.0),
                  const Divider(height: 1.0, color: AppColors.borderSubtle),
                  const SizedBox(height: 10.0),
                  Padding(
                    padding: const EdgeInsets.only(left: 48.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (nutrient.rdaPercentage != null) ...[
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Text(
                                'Adult Daily RDA Contribution:',
                                style: TextStyle(
                                  fontSize: 12.0,
                                  fontWeight: FontWeight.w500,
                                  color: AppColors.textSecondary,
                                ),
                              ),
                              Text(
                                '${nutrient.rdaPercentage!.toStringAsFixed(1)}%',
                                style: const TextStyle(
                                  fontSize: 12.0,
                                  fontWeight: FontWeight.w700,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4.0),
                        ],
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Data Status:',
                              style: TextStyle(
                                fontSize: 12.0,
                                fontWeight: FontWeight.w500,
                                color: AppColors.textSecondary,
                              ),
                            ),
                            Text(
                              nutrient.status,
                              style: const TextStyle(
                                fontSize: 11.0,
                                fontWeight: FontWeight.w600,
                                color: AppColors.textTertiary,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ClassificationBadge extends StatelessWidget {
  final String classification;

  const _ClassificationBadge({required this.classification});

  @override
  Widget build(BuildContext context) {
    Color bg = AppColors.unclassifiedBackground;
    Color text = AppColors.unclassified;
    Color border = AppColors.border;

    switch (classification.toLowerCase()) {
      case 'low':
        bg = AppColors.positiveBackground;
        text = AppColors.positive;
        border = AppColors.positiveBorder;
        break;
      case 'moderate':
        bg = AppColors.moderateBackground;
        text = AppColors.moderate;
        border = AppColors.moderateBorder;
        break;
      case 'high':
        bg = AppColors.concernBackground;
        text = AppColors.concern;
        border = AppColors.concernBorder;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 3.5),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(12.0),
        border: Border.all(color: border, width: 0.8),
      ),
      child: Text(
        classification,
        style: TextStyle(
          fontSize: 11.0,
          fontWeight: FontWeight.w700,
          color: text,
        ),
      ),
    );
  }
}

class _ThresholdScaleBar extends StatelessWidget {
  final double value;
  final double lowMax;
  final double moderateMax;
  final double highMin;

  const _ThresholdScaleBar({
    required this.value,
    required this.lowMax,
    required this.moderateMax,
    required this.highMin,
  });

  @override
  Widget build(BuildContext context) {
    // Normalization ratio across the 3 equal visual zones (Low: 0-0.33, Mod: 0.33-0.66, High: 0.66-1.0)
    double relativePos = 0.5;
    if (value <= lowMax) {
      relativePos = (lowMax > 0 ? (value / lowMax) : 0.5) * 0.33;
    } else if (value <= moderateMax) {
      final span = moderateMax - lowMax;
      relativePos = 0.33 + ((value - lowMax) / (span > 0 ? span : 1)) * 0.33;
    } else {
      final excess = value - moderateMax;
      relativePos = 0.66 + (excess / (moderateMax > 0 ? moderateMax : 10)).clamp(0.0, 1.0) * 0.34;
    }
    relativePos = relativePos.clamp(0.04, 0.96);

    return LayoutBuilder(
      builder: (context, constraints) {
        final totalWidth = constraints.maxWidth;
        final markerX = (totalWidth * relativePos) - 4.0;

        return SizedBox(
          height: 10.0,
          child: Stack(
            clipBehavior: Clip.none,
            alignment: Alignment.centerLeft,
            children: [
              // Segmented Bar (Green, Amber, Red)
              ClipRRect(
                borderRadius: BorderRadius.circular(5.0),
                child: SizedBox(
                  height: 6.0,
                  width: totalWidth,
                  child: const Row(
                    children: [
                      Expanded(
                        child: DecoratedBox(
                          decoration: BoxDecoration(color: Color(0xFF86EFAC)),
                        ),
                      ),
                      SizedBox(width: 1.5),
                      Expanded(
                        child: DecoratedBox(
                          decoration: BoxDecoration(color: Color(0xFFFCD34D)),
                        ),
                      ),
                      SizedBox(width: 1.5),
                      Expanded(
                        child: DecoratedBox(
                          decoration: BoxDecoration(color: Color(0xFFFCA5A5)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              // Pill Marker indicating actual value position
              Positioned(
                left: markerX,
                child: Container(
                  width: 8.0,
                  height: 12.0,
                  decoration: BoxDecoration(
                    color: AppColors.accentDark,
                    borderRadius: BorderRadius.circular(4.0),
                    border: Border.all(color: Colors.white, width: 1.2),
                  ),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

