import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class NutritionOverviewCard extends StatelessWidget {
  final List<NutrientItem> nutrients;
  final bool isPerServing;
  final String foodForm;

  const NutritionOverviewCard({
    super.key,
    required this.nutrients,
    required this.isPerServing,
    required this.foodForm,
  });

  NutrientItem? _findNutrient(List<String> codes) {
    for (final code in codes) {
      for (final n in nutrients) {
        if (n.nutrientCode.toLowerCase() == code.toLowerCase()) {
          return n;
        }
      }
    }
    return null;
  }

  String _formatValue(NutrientItem? item) {
    if (item == null) return '—';
    final val = isPerServing ? item.valuePerServing : item.valuePer100g;
    if (val == null) return '—';
    final formatted = val.toStringAsFixed(val.truncateToDouble() == val ? 0 : 1);
    return '$formatted ${item.unit}';
  }

  @override
  Widget build(BuildContext context) {
    final energy = _findNutrient(['energy', 'energy_kcal', 'calories']);
    final carbs = _findNutrient(['carbohydrates', 'carbs', 'total_carbohydrates']);
    final fat = _findNutrient(['total_fat', 'fat']);
    final sugar = _findNutrient(['total_sugars', 'sugars', 'sugar', 'added_sugars']);
    final protein = _findNutrient(['protein', 'proteins']);

    final basisText = isPerServing
        ? 'Energy / serving'
        : 'Energy / ${foodForm == 'liquid' ? '100 ml' : '100 g'}';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section Header
        const Text('Nutrition Overview', style: AppTypography.h2),
        const SizedBox(height: 2.0),
        const Text('Key nutrients and energy content', style: AppTypography.bodyMedium),
        const SizedBox(height: AppSpacing.md),

        // Horizontal Row: Energy Hero Card + 4 Mini Cards
        LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              clipBehavior: Clip.none,
              child: Row(
                children: [
                  // Energy Hero Card
                  Container(
                    width: 140.0,
                    height: 96.0,
                    padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: AppColors.energyGradient,
                      ),
                      borderRadius: AppSpacing.borderRadiusCard,
                      border: Border.all(color: AppColors.border, width: 0.8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Icon(
                          Icons.bolt_rounded,
                          size: 18.0,
                          color: AppColors.brandOrange,
                        ),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            RichText(
                              text: TextSpan(
                                style: const TextStyle(
                                  fontSize: 18.0,
                                  fontWeight: FontWeight.w800,
                                  color: AppColors.textPrimary,
                                  fontFamily: 'sans-serif',
                                ),
                                children: [
                                  TextSpan(
                                    text: energy != null
                                        ? ((isPerServing ? energy.valuePerServing : energy.valuePer100g)
                                                ?.toStringAsFixed(0) ??
                                            '—')
                                        : '—',
                                  ),
                                  const TextSpan(
                                    text: ' kcal',
                                    style: TextStyle(
                                      fontSize: 12.0,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 1.0),
                            Text(
                              basisText,
                              style: const TextStyle(
                                fontSize: 10.5,
                                fontWeight: FontWeight.w500,
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: AppSpacing.sm),

                  // Mini Nutrient Cards
                  _MiniNutrientCard(
                    title: 'Carbs',
                    value: _formatValue(carbs),
                    icon: Icons.grain_rounded,
                    iconColor: AppColors.nutrientCarbs,
                    iconBgColor: AppColors.nutrientCarbsBg,
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  _MiniNutrientCard(
                    title: 'Fat',
                    value: _formatValue(fat),
                    icon: Icons.water_drop_rounded,
                    iconColor: AppColors.nutrientFat,
                    iconBgColor: AppColors.nutrientFatBg,
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  _MiniNutrientCard(
                    title: 'Sugar',
                    value: _formatValue(sugar),
                    icon: Icons.view_in_ar_rounded,
                    iconColor: AppColors.nutrientSugar,
                    iconBgColor: AppColors.nutrientSugarBg,
                  ),
                  const SizedBox(width: AppSpacing.sm),
                  _MiniNutrientCard(
                    title: 'Protein',
                    value: _formatValue(protein),
                    icon: Icons.fitness_center_rounded,
                    iconColor: AppColors.nutrientProtein,
                    iconBgColor: AppColors.nutrientProteinBg,
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }
}

class _MiniNutrientCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color iconColor;
  final Color iconBgColor;

  const _MiniNutrientCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.iconColor,
    required this.iconBgColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 78.0,
      height: 96.0,
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 10.0),
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: AppColors.border, width: 0.8),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Circular Icon Container
          Container(
            width: 30.0,
            height: 30.0,
            decoration: BoxDecoration(
              color: iconBgColor,
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Icon(icon, size: 16.0, color: iconColor),
          ),
          Column(
            children: [
              Text(
                title,
                style: const TextStyle(
                  fontSize: 10.5,
                  fontWeight: FontWeight.w500,
                  color: AppColors.textSecondary,
                ),
                maxLines: 1,
              ),
              const SizedBox(height: 1.0),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 13.0,
                  fontWeight: FontWeight.w700,
                  color: AppColors.textPrimary,
                ),
                maxLines: 1,
              ),
            ],
          ),
        ],
      ),
    );
  }
}

