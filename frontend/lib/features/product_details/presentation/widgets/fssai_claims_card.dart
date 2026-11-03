import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class FssaiClaimsCard extends StatelessWidget {
  final RegulatoryClaimsValidation? claimsValidation;
  final VoidCallback? onNavigateToDetails;

  const FssaiClaimsCard({
    super.key,
    this.claimsValidation,
    this.onNavigateToDetails,
  });

  @override
  Widget build(BuildContext context) {
    final claims = claimsValidation?.claims ?? [];

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onNavigateToDetails,
          borderRadius: AppSpacing.borderRadiusCard,
          child: Padding(
            padding: const EdgeInsets.all(AppSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header with navigation chevron
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.balance_rounded, size: 16.0, color: Color(0xFFD97706)),
                        SizedBox(width: 6.0),
                        Text('FSSAI Claim Verification', style: AppTypography.h3),
                      ],
                    ),
                    Icon(
                      Icons.chevron_right_rounded,
                      size: 20.0,
                      color: AppColors.textTertiary,
                    ),
                  ],
                ),
                const SizedBox(height: AppSpacing.md),

                if (claims.isEmpty) ...[
                  const Text(
                    'No statutory claims evaluated or declared for this product category.',
                    style: TextStyle(
                      fontSize: 11.5,
                      color: AppColors.textSecondary,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ] else ...[
                  ...claims.take(3).map((claim) => _ClaimRow(claim: claim)),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ClaimRow extends StatelessWidget {
  final RegulatoryClaimItem claim;

  const _ClaimRow({required this.claim});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color iconColor;
    String statusText;

    switch (claim.status.toUpperCase()) {
      case 'COMPLIANT':
      case 'VALID':
      case 'ELIGIBLE':
        icon = Icons.check_circle_rounded;
        iconColor = AppColors.positive;
        statusText = 'Valid';
        break;
      case 'NOT_COMPLIANT':
      case 'INELIGIBLE':
        icon = Icons.cancel_rounded;
        iconColor = AppColors.concern;
        statusText = 'Non-compliant';
        break;
      case 'INSUFFICIENT_DATA':
        icon = Icons.help_rounded;
        iconColor = AppColors.moderate;
        statusText = 'Insufficient data';
        break;
      case 'NOT_CLAIMED':
      default:
        icon = Icons.remove_circle_outline_rounded;
        iconColor = AppColors.textTertiary;
        statusText = 'Not claimed';
        break;
    }

    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Row(
        children: [
          Icon(icon, size: 15.0, color: iconColor),
          const SizedBox(width: 6.0),
          Expanded(
            child: Text(
              '${claim.claimName} – $statusText',
              style: const TextStyle(
                fontSize: 12.0,
                fontWeight: FontWeight.w500,
                color: AppColors.textPrimary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}
