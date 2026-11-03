import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

class HomePlaceholderScreen extends StatelessWidget {
  final VoidCallback? onScanProduct;

  const HomePlaceholderScreen({super.key, this.onScanProduct});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Home (Integration Point)', style: AppTypography.h3),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.home_outlined, size: 48.0, color: AppColors.textTertiary),
              const SizedBox(height: 16.0),
              const Text('Home Screen Placeholder', style: AppTypography.h2),
              const SizedBox(height: 8.0),
              const Text(
                'Prepared for future Phase. Currently focusing on the Nutrition Visualization / Product Details screen.',
                style: AppTypography.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24.0),
              ElevatedButton.icon(
                onPressed: onScanProduct,
                icon: const Icon(Icons.qr_code_scanner_rounded),
                label: const Text('Open Product Nutrition Screen'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

