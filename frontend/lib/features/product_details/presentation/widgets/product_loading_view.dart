import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';

class ProductLoadingView extends StatelessWidget {
  const ProductLoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 56.0,
            height: 56.0,
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.border, width: 1.0),
            ),
            child: const CircularProgressIndicator(
              strokeWidth: 2.5,
              color: AppColors.brandOrange,
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          const Text(
            'Analyzing Nutrition Data...',
            style: TextStyle(
              fontSize: 14.0,
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 4.0),
          const Text(
            'Evaluating FSSAI claims & ICMR-NIN thresholds',
            style: TextStyle(
              fontSize: 12.0,
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

