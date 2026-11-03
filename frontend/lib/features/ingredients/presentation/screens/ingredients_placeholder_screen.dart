import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

class IngredientsPlaceholderScreen extends StatelessWidget {
  const IngredientsPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Ingredient Details', style: AppTypography.h3)),
      body: const Center(
        child: Text('Detailed Ingredient Taxonomy integration point prepared.', style: AppTypography.bodyMedium),
      ),
    );
  }
}

