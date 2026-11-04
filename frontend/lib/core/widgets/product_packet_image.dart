import 'package:flutter/material.dart';
import '../config/env_config.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';

/// Renders a cleanly cropped product packet image without background clutter.
///
/// Multi-tier resolution strategy:
/// 1. Direct local Flutter asset if path starts with `assets/`
/// 2. Local bundled packet asset (`assets/images/products/<barcode>.png`) for zero-latency offline loading
/// 3. Backend static image endpoint (`${EnvConfig.baseUrl}/static/products/...`)
/// 4. Graceful category packet visual fallback (`assets/images/cat_*.webp`)
class ProductPacketImage extends StatelessWidget {
  final String? imageUrl;
  final String? barcode;
  final String? category;
  final double? width;
  final double? height;
  final BoxFit fit;
  final BorderRadius? borderRadius;
  final Color? backgroundColor;

  const ProductPacketImage({
    super.key,
    this.imageUrl,
    this.barcode,
    this.category,
    this.width,
    this.height,
    this.fit = BoxFit.contain,
    this.borderRadius,
    this.backgroundColor,
  });

  String _getCategoryFallback() {
    final cat = (category ?? '').toLowerCase();
    if (cat.contains('biscuit') || cat.contains('cookie') || cat.contains('bakery') || cat.contains('wafer')) {
      return 'assets/images/cat_biscuits.webp';
    }
    if (cat.contains('beverage') || cat.contains('drink') || cat.contains('juice') || cat.contains('cola') || cat.contains('tea') || cat.contains('sauce') || cat.contains('ketchup')) {
      return 'assets/images/cat_beverages.webp';
    }
    if (cat.contains('dairy') || cat.contains('milk') || cat.contains('butter') || cat.contains('cheese') || cat.contains('paneer')) {
      return 'assets/images/cat_dairy.webp';
    }
    return 'assets/images/cat_snacks.webp';
  }

  String? _resolveAssetPath() {
    if (imageUrl != null && imageUrl!.startsWith('assets/')) {
      return imageUrl;
    }
    // Extract barcode from URL if available
    final b = barcode ?? _extractBarcode(imageUrl);
    if (b != null && b.isNotEmpty) {
      // Known demo product barcodes bundled locally
      const bundledBarcodes = {
        '8901063142022', '8901030383701',
        '8901058851298', '8901058860002',
        '8901233023724', '8901233024013',
        '8906010500863',
        '8901764061103',
        '7622201756697',
        '8901491101837', '8901491101838',
        '8901491100519',
        '8901719100956',
        '8904063218124', '8904063200150',
        '8901058868036',
        '8901030825279',
        '8901262010017',
      };
      if (bundledBarcodes.contains(b)) {
        return 'assets/images/products/$b.png';
      }
    }
    return null;
  }

  String? _extractBarcode(String? url) {
    if (url == null) return null;
    final match = RegExp(r'(\d{8,14})').firstMatch(url);
    return match?.group(1);
  }

  String? _resolveNetworkUrl() {
    if (imageUrl == null || imageUrl!.trim().isEmpty) return null;
    final trimmed = imageUrl!.trim();
    if (trimmed.startsWith('assets/')) return null;
    if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
      return trimmed;
    }
    if (trimmed.startsWith('/')) {
      return '${EnvConfig.baseUrl}$trimmed';
    }
    return '${EnvConfig.baseUrl}/$trimmed';
  }

  Widget _buildFallback(BuildContext context) {
    final asset = _getCategoryFallback();
    return Image.asset(
      asset,
      width: width,
      height: height,
      fit: fit,
      errorBuilder: (_, __, ___) => const Center(
        child: Icon(
          Icons.inventory_2_outlined,
          color: AppColors.textTertiary,
          size: 28.0,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final assetPath = _resolveAssetPath();
    final networkUrl = _resolveNetworkUrl();

    Widget content;
    if (assetPath != null) {
      content = Image.asset(
        assetPath,
        width: width,
        height: height,
        fit: fit,
        errorBuilder: (_, __, ___) => _buildFallback(context),
      );
    } else if (networkUrl != null) {
      content = Image.network(
        networkUrl,
        width: width,
        height: height,
        fit: fit,
        errorBuilder: (_, __, ___) => _buildFallback(context),
        loadingBuilder: (context, child, loadingProgress) {
          if (loadingProgress == null) return child;
          return Center(
            child: SizedBox(
              width: 18.0,
              height: 18.0,
              child: CircularProgressIndicator(
                strokeWidth: 2.0,
                color: AppColors.brandOrange.withValues(alpha: 0.6),
              ),
            ),
          );
        },
      );
    } else {
      content = _buildFallback(context);
    }

    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: backgroundColor ?? AppColors.surfaceSubtle,
        borderRadius: borderRadius ?? BorderRadius.circular(AppSpacing.radiusMd),
      ),
      clipBehavior: Clip.antiAlias,
      child: content,
    );
  }
}
