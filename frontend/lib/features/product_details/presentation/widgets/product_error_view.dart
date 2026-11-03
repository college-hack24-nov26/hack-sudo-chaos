import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../../../core/network/api_exceptions.dart';

class ProductErrorView extends StatelessWidget {
  final Object error;
  final VoidCallback onRetry;

  const ProductErrorView({
    super.key,
    required this.error,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    IconData icon = Icons.cloud_off_rounded;
    String title = 'Connection Failed';
    String description =
        'Could not communicate with YumSure server. Please verify your backend server is running and device has network connectivity.';

    if (error is ProductNotFoundException) {
      icon = Icons.search_off_rounded;
      title = 'Product Not Found';
      description =
          'This barcode is not yet indexed in our local database or Open Food Facts. You can contribute packaging photos later.';
    } else if (error is ApiException) {
      final apiErr = error as ApiException;
      title = apiErr.errorType ?? 'API Error';
      description = apiErr.message;
    }

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSpacing.xxl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 64.0,
              height: 64.0,
              decoration: const BoxDecoration(
                color: Color(0xFFFEF2F2),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, size: 32.0, color: AppColors.concern),
            ),
            const SizedBox(height: AppSpacing.lg),
            Text(title, style: AppTypography.h2, textAlign: TextAlign.center),
            const SizedBox(height: AppSpacing.sm),
            Text(
              description,
              style: AppTypography.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppSpacing.xl),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded, size: 18.0),
              label: const Text('Try Again'),
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.accentDark,
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

