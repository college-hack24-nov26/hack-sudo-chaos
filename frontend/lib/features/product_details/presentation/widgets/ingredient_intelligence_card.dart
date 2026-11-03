import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class IngredientIntelligenceCard extends StatelessWidget {
  final IngredientAnalysis? ingredientAnalysis;
  final VoidCallback? onNavigateToDetails;

  const IngredientIntelligenceCard({
    super.key,
    this.ingredientAnalysis,
    this.onNavigateToDetails,
  });

  @override
  Widget build(BuildContext context) {
    final hasData = ingredientAnalysis != null &&
        (ingredientAnalysis!.categories.isNotEmpty ||
            (ingredientAnalysis!.ingredientsSummary != null &&
                ingredientAnalysis!.ingredientsSummary!.isNotEmpty));

    // Extract up to 3 highlighted ingredient names
    final highlightedChips = <String>[];
    if (ingredientAnalysis != null) {
      for (final cat in ingredientAnalysis!.categories) {
        for (final item in cat.items) {
          if (highlightedChips.length < 3) {
            highlightedChips.add(item);
          }
        }
      }
    }

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onNavigateToDetails,
          borderRadius: AppSpacing.borderRadiusCard,
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header with navigation chevron
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.eco_rounded, size: 16.0, color: AppColors.positive),
                        SizedBox(width: 6.0),
                        Text('Ingredient Intelligence', style: AppTypography.h3),
                      ],
                    ),
                    Icon(
                      Icons.chevron_right_rounded,
                      size: 20.0,
                      color: AppColors.textTertiary,
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.sm),

                if (!hasData) ...[
                  const Text(
                    'Ingredient list is not declared or not yet indexed for this product.',
                    style: TextStyle(
                      fontSize: 12.0,
                      color: AppColors.textSecondary,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ] else ...[
                  // Highlighted Ingredient Chips
                  if (highlightedChips.isNotEmpty) ...[
                    Wrap(
                      spacing: 6.0,
                      runSpacing: 4.0,
                      children: highlightedChips.map((chip) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEE2E2), // Soft pink/red tint
                            borderRadius: BorderRadius.circular(10.0),
                            border: Border.all(color: const Color(0xFFFECACA), width: 0.8),
                          ),
                          child: Text(
                            chip,
                            style: const TextStyle(
                              fontSize: 10.5,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFFDC2626),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: AppSpacing.sm),
                  ],
                  // Summary Explanation
                  Text(
                    ingredientAnalysis!.ingredientsSummary ??
                        'Identified ${ingredientAnalysis!.totalIngredientsCount} declared ingredients across ${ingredientAnalysis!.categories.length} functional classifications.',
                    style: AppTypography.bodySmall,
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
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
