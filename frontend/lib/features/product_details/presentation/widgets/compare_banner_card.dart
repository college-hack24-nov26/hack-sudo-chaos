import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';

class CompareBannerCard extends StatelessWidget {
  final VoidCallback? onCompare;

  const CompareBannerCard({super.key, this.onCompare});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
      child: Row(
        children: [
          // Bar Chart Icon
          Container(
            width: 36.0,
            height: 36.0,
            decoration: BoxDecoration(
              color: AppColors.accentLavenderLight,
              borderRadius: BorderRadius.circular(10.0),
            ),
            alignment: Alignment.center,
            child: const Icon(
              Icons.bar_chart_rounded,
              size: 20.0,
              color: AppColors.accentPurple,
            ),
          ),
          const SizedBox(width: AppSpacing.md),
          // Texts
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Compare this product', style: AppTypography.h3),
                SizedBox(height: 2.0),
                Text(
                  'See how it fares against similar products.',
                  style: TextStyle(
                    fontSize: 11.5,
                    color: AppColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: AppSpacing.sm),
          // Compare Button
          ElevatedButton(
            onPressed: onCompare,
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.accentDark,
              padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 8.0),
              minimumSize: const Size(0, 36.0),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppSpacing.radiusPill),
              ),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Compare',
                  style: TextStyle(fontSize: 12.0, fontWeight: FontWeight.w700),
                ),
                SizedBox(width: 4.0),
                Icon(Icons.arrow_forward_rounded, size: 14.0),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

