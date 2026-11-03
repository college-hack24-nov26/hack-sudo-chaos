import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

class ScannerPlaceholderScreen extends StatelessWidget {
  const ScannerPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('Scanner', style: AppTypography.h3)),
      body: const Center(
        child: Text('Barcode Scanner camera integration point prepared.', style: AppTypography.bodyMedium),
      ),
    );
  }
}

