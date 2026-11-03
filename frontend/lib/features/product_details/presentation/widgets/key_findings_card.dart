import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class KeyFindingsCard extends StatelessWidget {
  final List<KeyFindingItem> findings;

  const KeyFindingsCard({super.key, required this.findings});

  @override
  Widget build(BuildContext context) {
    // Show maximum 3 key findings
    final displayFindings = findings.take(3).toList();

    return Container(
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
          const Row(
            children: [
              Icon(Icons.auto_awesome_rounded, size: 16.0, color: AppColors.brandOrange),
              SizedBox(width: 6.0),
              Text('Key Findings', style: AppTypography.h3),
            ],
          ),
          const SizedBox(height: AppSpacing.md),
          if (displayFindings.isEmpty) ...[
            const Text(
              'No significant nutrient anomalies flagged for this product.',
              style: TextStyle(fontSize: 12.0, color: AppColors.textSecondary, fontStyle: FontStyle.italic),
            ),
          ] else ...[
            ...displayFindings.map((finding) => _FindingRow(finding: finding)),
          ],
        ],
      ),
    );
  }
}

class _FindingRow extends StatelessWidget {
  final KeyFindingItem finding;

  const _FindingRow({required this.finding});

  @override
  Widget build(BuildContext context) {
    IconData iconData = Icons.info_outline_rounded;
    Color iconColor = AppColors.neutral;

    switch (finding.severity.toUpperCase()) {
      case 'HIGH':
        iconData = Icons.error_rounded;
        iconColor = AppColors.concern;
        break;
      case 'MODERATE':
        iconData = Icons.warning_rounded;
        iconColor = AppColors.moderate;
        break;
      case 'POSITIVE':
        iconData = Icons.check_circle_rounded;
        iconColor = AppColors.positive;
        break;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(iconData, size: 16.0, color: iconColor),
          const SizedBox(width: 8.0),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(
                  fontSize: 12.0,
                  color: AppColors.textPrimary,
                  height: 1.35,
                  fontFamily: 'sans-serif',
                ),
                children: [
                  TextSpan(
                    text: '${finding.title} ',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  TextSpan(
                    text: '(${finding.valueText})',
                    style: const TextStyle(color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

