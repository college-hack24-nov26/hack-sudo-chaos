import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

class AiExplanationPlaceholderScreen extends StatelessWidget {
  const AiExplanationPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('AI Food Explanation', style: AppTypography.h3)),
      body: const Center(
        child: Text('AI Food Explanation screen integration point prepared.', style: AppTypography.bodyMedium),
      ),
    );
  }
}

