import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class AllergenCard extends StatelessWidget {
  final IngredientAnalysis? ingredientAnalysis;
  final String? barcode;
  final VoidCallback? onTap;

  const AllergenCard({
    super.key,
    this.ingredientAnalysis,
    this.barcode,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final declared = ingredientAnalysis?.declaredAllergens ?? [];
    final mayContain = ingredientAnalysis?.mayContainAllergens ?? [];

    return GestureDetector(
      onTap: onTap ??
          (barcode != null && barcode!.isNotEmpty
              ? () => context.push('/product/$barcode/allergens')
              : null),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surfaceCard,
          borderRadius: AppSpacing.borderRadiusCard,
          border: Border.all(color: AppColors.border, width: 1.0),
        ),
      padding: const EdgeInsets.all(AppSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              const Icon(Icons.shield_outlined, size: 16.0, color: AppColors.concern),
              const SizedBox(width: 6.0),
              const Expanded(
                child: Text('Allergen Information', style: AppTypography.h3),
              ),
              if (barcode != null || onTap != null)
                const Icon(
                  Icons.chevron_right_rounded,
                  size: 20.0,
                  color: AppColors.textSecondary,
                ),
            ],
          ),
          const SizedBox(height: AppSpacing.md),

          if (declared.isEmpty && mayContain.isEmpty) ...[
            const Text(
              'No statutory allergens explicitly declared on packaging. Check packaging if you have severe allergies.',
              style: TextStyle(
                fontSize: 11.5,
                color: AppColors.textSecondary,
                fontStyle: FontStyle.italic,
              ),
            ),
          ] else ...[
            // Declared Allergens (Contains)
            if (declared.isNotEmpty) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 6.0),
                decoration: BoxDecoration(
                  color: AppColors.concernBackground,
                  borderRadius: BorderRadius.circular(10.0),
                  border: Border.all(color: AppColors.concernBorder, width: 0.8),
                ),
                child: RichText(
                  text: TextSpan(
                    style: const TextStyle(
                      fontSize: 11.5,
                      fontFamily: 'sans-serif',
                      color: Color(0xFFDC2626),
                    ),
                    children: [
                      const TextSpan(
                        text: 'Contains: ',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                      TextSpan(text: declared.join(', ')),
                    ],
                  ),
                ),
              ),
            ],
            if (declared.isNotEmpty && mayContain.isNotEmpty) const SizedBox(height: 6.0),
            // Cross-contamination warning (May contain)
            if (mayContain.isNotEmpty) ...[
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 6.0),
                decoration: BoxDecoration(
                  color: AppColors.moderateBackground,
                  borderRadius: BorderRadius.circular(10.0),
                  border: Border.all(color: AppColors.moderateBorder, width: 0.8),
                ),
                child: RichText(
                  text: TextSpan(
                    style: const TextStyle(
                      fontSize: 11.5,
                      fontFamily: 'sans-serif',
                      color: Color(0xFFD97706),
                    ),
                    children: [
                      const TextSpan(
                        text: 'May contain: ',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                      TextSpan(text: mayContain.join(', ')),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ],
      ),
      ),
    );
  }
}

