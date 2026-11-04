import '../../../../core/widgets/product_packet_image.dart';
import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/home_models.dart';

class RecentScansSection extends StatelessWidget {
  final List<ScanHistoryItem> scans;
  final Object? error;
  final ValueChanged<String> onProductTapped;
  final VoidCallback? onSeeAll;
  final VoidCallback onScanProduct;
  final VoidCallback? onRetry;

  const RecentScansSection({
    super.key,
    required this.scans,
    this.error,
    required this.onProductTapped,
    this.onSeeAll,
    required this.onScanProduct,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section Header Row
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                'Recent Scans',
                style: TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: 16.0,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF141414),
                  letterSpacing: -0.2,
                ),
              ),
              InkWell(
                onTap: onSeeAll,
                borderRadius: BorderRadius.circular(8.0),
                child: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 4.0, vertical: 2.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        'See all',
                        style: TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 12.0,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF6E6877),
                        ),
                      ),
                      SizedBox(width: 3.0),
                      Icon(Icons.arrow_forward_rounded, size: 13.0, color: Color(0xFF6E6877)),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12.0),

        // Body: Single Continuous Card Container Matching Reference
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: _buildContent(),
        ),
      ],
    );
  }

  Widget _buildContent() {
    // 1. Error condition: Compact offline status inside continuous card
    if (error != null) {
      return _RecentScansOfflineCard(onRetry: onRetry);
    }

    // 2. HTTP 200 with scanned items: Continuous white card with hairlines
    if (scans.isNotEmpty) {
      return Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(22.0),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0A000000),
              blurRadius: 10.0,
              offset: Offset(0, 3),
            ),
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Column(
          children: [
            for (int i = 0; i < scans.length; i++) ...[
              if (i > 0)
                const Divider(
                  height: 1.0,
                  thickness: 0.8,
                  color: Color(0xFFF4EEE8),
                  indent: 14.0,
                  endIndent: 14.0,
                ),
              _RecentScanRow(
                item: scans[i],
                onTap: () => onProductTapped(scans[i].barcode),
              ),
            ],
          ],
        ),
      );
    }

    // 3. HTTP 200 with empty list: legitimate empty state
    return _RecentScansEmptyCard(onScanProduct: onScanProduct);
  }
}

class _RecentScansOfflineCard extends StatelessWidget {
  final VoidCallback? onRetry;

  const _RecentScansOfflineCard({this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFBF8F6),
        borderRadius: BorderRadius.circular(22.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 10.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(
            Icons.wifi_off_rounded,
            size: 16.0,
            color: Color(0xFF8E8A93),
          ),
          const SizedBox(width: 10.0),
          const Expanded(
            child: Text(
              'History offline (backend unreachable)',
              style: TextStyle(
                fontFamily: AppTypography.fontFamily,
                fontSize: 12.0,
                fontWeight: FontWeight.w500,
                color: Color(0xFF6E6877),
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (onRetry != null)
            Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onRetry,
                borderRadius: BorderRadius.circular(8.0),
                child: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.refresh_rounded, size: 14.0, color: AppColors.brandOrange),
                      SizedBox(width: 3.0),
                      Text(
                        'Retry',
                        style: TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 12.0,
                          fontWeight: FontWeight.w700,
                          color: AppColors.brandOrange,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class _RecentScanRow extends StatelessWidget {
  final ScanHistoryItem item;
  final VoidCallback onTap;

  const _RecentScanRow({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 11.0),
          child: Row(
            children: [
              // 1. Product Thumbnail
              _ScanThumbnail(imageUrl: item.imageUrl, barcode: item.barcode),
              const SizedBox(width: 12.0),

              // 2. Product Name & Category / Scan Time
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      item.productName,
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 13.5,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF141414),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2.0),
                    Text(
                      '${item.foodCategory} • ${item.relativeTimeFormatted}',
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 11.0,
                        color: Color(0xFF6E6877),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 8.0),

              // 3. Finding Badge
              if (item.keyFinding != null && item.keyFinding!.isNotEmpty) ...[
                _FindingBadge(
                  text: item.keyFinding!,
                  severity: item.keyFindingSeverity ?? 'MODERATE',
                ),
                const SizedBox(width: 6.0),
              ],

              // 4. Chevron Navigation Indicator
              const Icon(
                Icons.chevron_right_rounded,
                size: 18.0,
                color: Color(0xFF6E6877),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ScanThumbnail extends StatelessWidget {
  final String? imageUrl;
  final String? barcode;

  const _ScanThumbnail({this.imageUrl, this.barcode});

  @override
  Widget build(BuildContext context) {
    return ProductPacketImage(
      imageUrl: imageUrl,
      barcode: barcode,
      width: 38.0,
      height: 38.0,
      fit: BoxFit.contain,
      borderRadius: BorderRadius.circular(10.0),
      backgroundColor: const Color(0xFFFAF6F2),
    );
  }
}

class _FindingBadge extends StatelessWidget {
  final String text;
  final String severity;

  const _FindingBadge({required this.text, required this.severity});

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    IconData icon;

    switch (severity.toUpperCase()) {
      case 'HIGH':
        bg = const Color(0xFFFFECEB);
        fg = const Color(0xFFE53935);
        icon = Icons.error_rounded;
        break;
      case 'MODERATE':
        bg = const Color(0xFFFFF3E0);
        fg = const Color(0xFFF57C00);
        icon = Icons.warning_rounded;
        break;
      case 'LOW':
      default:
        bg = const Color(0xFFE8F5E9);
        fg = const Color(0xFF2E7D32);
        icon = Icons.check_circle_rounded;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 3.5),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(12.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12.0, color: fg),
          const SizedBox(width: 4.0),
          Text(
            text,
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 10.5,
              fontWeight: FontWeight.w700,
              color: fg,
            ),
          ),
        ],
      ),
    );
  }
}

class _RecentScansEmptyCard extends StatelessWidget {
  final VoidCallback onScanProduct;

  const _RecentScansEmptyCard({required this.onScanProduct});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 20.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 10.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        children: [
          const Text(
            'No scans yet',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 14.5,
              fontWeight: FontWeight.w700,
              color: Color(0xFF141414),
            ),
          ),
          const SizedBox(height: 4.0),
          const Text(
            'Scan your first packaged food product to see its ingredients and nutritional evaluation here.',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 11.5,
              color: Color(0xFF6E6877),
              height: 1.35,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12.0),
          OutlinedButton.icon(
            onPressed: onScanProduct,
            icon: const Icon(Icons.qr_code_scanner_rounded, size: 16.0),
            label: const Text(
              'Scan a Product',
              style: TextStyle(
                fontFamily: AppTypography.fontFamily,
                fontSize: 12.0,
                fontWeight: FontWeight.w700,
              ),
            ),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF141414),
              side: const BorderSide(color: Color(0xFFEAE3DB), width: 1.0),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            ),
          ),
        ],
      ),
    );
  }
}
