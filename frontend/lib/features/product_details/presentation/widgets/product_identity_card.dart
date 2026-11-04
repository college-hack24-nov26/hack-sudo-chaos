import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../../../core/widgets/product_packet_image.dart';
import '../../data/models/product_response_model.dart';

class ProductIdentityCard extends StatelessWidget {
  final ProductIdentity product;
  final bool? isFssaiCompliant;

  const ProductIdentityCard({
    super.key,
    required this.product,
    this.isFssaiCompliant,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceCard,
        borderRadius: AppSpacing.borderRadiusCard,
        border: Border.all(color: AppColors.border, width: 1.0),
      ),
      padding: const EdgeInsets.all(AppSpacing.lg),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Product Image or Neutral Placeholder
          _ProductThumbnail(imageUrl: product.imageUrl, barcode: product.barcode, category: product.foodCategory),
          const SizedBox(width: AppSpacing.md),
          // Product Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top Row: Badges
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Wrap(
                      spacing: 6.0,
                      runSpacing: 4.0,
                      children: [
                        if (isFssaiCompliant == true)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
                            decoration: BoxDecoration(
                              color: AppColors.positiveBackground,
                              borderRadius: BorderRadius.circular(12.0),
                              border: Border.all(color: AppColors.positiveBorder, width: 0.8),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.check_circle_rounded, size: 12.0, color: AppColors.positive),
                                SizedBox(width: 4.0),
                                Text(
                                  'FSSAI Compliant',
                                  style: TextStyle(
                                    fontSize: 10.5,
                                    fontWeight: FontWeight.w700,
                                    color: AppColors.positive,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.0),
                          decoration: BoxDecoration(
                            color: product.isVerified ? const Color(0xFFE8F5E9) : const Color(0xFFFFF8E1),
                            borderRadius: BorderRadius.circular(12.0),
                            border: Border.all(
                              color: product.isVerified ? const Color(0xFFA5D6A7) : const Color(0xFFFFE082),
                              width: 0.8,
                            ),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                product.isVerified ? Icons.verified_rounded : Icons.info_outline_rounded,
                                size: 12.0,
                                color: product.isVerified ? const Color(0xFF2E7D32) : const Color(0xFFF57F17),
                              ),
                              const SizedBox(width: 4.0),
                              Text(
                                product.isVerified ? 'Verified' : 'Unverified',
                                style: TextStyle(
                                  fontSize: 10.5,
                                  fontWeight: FontWeight.w700,
                                  color: product.isVerified ? const Color(0xFF2E7D32) : const Color(0xFFF57F17),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    // Indian Veg / Non-Veg Indicator
                    if (product.isVeg != null) _VegIndicator(isVeg: product.isVeg!),
                  ],
                ),
                const SizedBox(height: AppSpacing.xs),
                // Product Name
                Text(
                  product.productName,
                  style: AppTypography.h2,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                if (product.brandName != null && product.brandName!.isNotEmpty) ...[
                  const SizedBox(height: 2.0),
                  Text(
                    product.brandName!,
                    style: AppTypography.bodyMedium,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
                const SizedBox(height: AppSpacing.sm),
                // Category & Tag Chips
                Wrap(
                  spacing: 6.0,
                  runSpacing: 4.0,
                  children: [
                    if (product.foodCategory != null && product.foodCategory!.isNotEmpty)
                      _CategoryChip(label: product.foodCategory!),
                    _CategoryChip(
                      label: product.foodForm == 'liquid' ? 'Beverage' : 'Packaged Food',
                    ),
                    if (product.packageSize != null && product.packageSize!.isNotEmpty)
                      _CategoryChip(label: product.packageSize!),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ProductThumbnail extends StatelessWidget {
  final String? imageUrl;
  final String? barcode;
  final String? category;

  const _ProductThumbnail({this.imageUrl, this.barcode, this.category});

  @override
  Widget build(BuildContext context) {
    return ProductPacketImage(
      imageUrl: imageUrl,
      barcode: barcode,
      category: category,
      width: 76.0,
      height: 76.0,
      fit: BoxFit.contain,
      borderRadius: BorderRadius.circular(AppSpacing.radiusMd),
    );
  }
}


class _CategoryChip extends StatelessWidget {
  final String label;

  const _CategoryChip({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.5),
      decoration: BoxDecoration(
        color: AppColors.surfaceSubtle,
        borderRadius: BorderRadius.circular(10.0),
        border: Border.all(color: AppColors.border, width: 0.8),
      ),
      child: Text(
        label,
        style: const TextStyle(
          fontSize: 11.0,
          fontWeight: FontWeight.w500,
          color: AppColors.textSecondary,
        ),
      ),
    );
  }
}

class _VegIndicator extends StatelessWidget {
  final bool isVeg;

  const _VegIndicator({required this.isVeg});

  @override
  Widget build(BuildContext context) {
    final color = isVeg ? const Color(0xFF16A34A) : const Color(0xFFDC2626);
    return Tooltip(
      message: isVeg ? 'Vegetarian' : 'Non-Vegetarian',
      child: Container(
        width: 16.0,
        height: 16.0,
        decoration: BoxDecoration(
          border: Border.all(color: color, width: 1.5),
          borderRadius: BorderRadius.circular(3.0),
        ),
        alignment: Alignment.center,
        child: Container(
          width: 8.0,
          height: 8.0,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
