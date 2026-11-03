import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

class ComparisonPlaceholderScreen extends StatelessWidget {
  const ComparisonPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Product Comparison', style: AppTypography.h3)),
      body: const Center(
        child: Text('Product Comparison screen integration point prepared.', style: AppTypography.bodyMedium),
      ),
    );
  }
}

