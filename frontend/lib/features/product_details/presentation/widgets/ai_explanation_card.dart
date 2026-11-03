import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class AiExplanationCard extends StatelessWidget {
  final AiExplanation? aiExplanation;
  final VoidCallback? onNavigateToFullExplanation;

  const AiExplanationCard({
    super.key,
    this.aiExplanation,
    this.onNavigateToFullExplanation,
  });

  @override
  Widget build(BuildContext context) {
    if (aiExplanation == null || aiExplanation!.text.trim().isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFFFBF8FD), // Subtle lavender-tinted background
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: const Color(0xFFE9D8FD), width: 1.0),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onNavigateToFullExplanation,
          borderRadius: AppSpacing.borderRadiusCard,
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Header Row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.auto_awesome_rounded, size: 16.0, color: AppColors.accentPurple),
                        SizedBox(width: 6.0),
                        Text('AI Explanation', style: AppTypography.h3),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 2.5),
                      decoration: BoxDecoration(
                        color: AppColors.accentPurple,
                        borderRadius: BorderRadius.circular(10.0),
                      ),
                      child: const Text(
                        'AI',
                        style: TextStyle(
                          fontSize: 10.0,
                          fontWeight: FontWeight.w800,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.sm),
                // Body Text
                Text(
                  aiExplanation!.text,
                  style: AppTypography.bodySmall.copyWith(
                    color: AppColors.textPrimary,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

