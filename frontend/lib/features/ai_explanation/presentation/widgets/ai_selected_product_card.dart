import 'package:flutter/material.dart';
import '../../../product_details/data/models/product_response_model.dart';

class AiSelectedProductCard extends StatefulWidget {
  final ProductDetailsResponse? product;

  const AiSelectedProductCard({
    super.key,
    required this.product,
  });

  @override
  State<AiSelectedProductCard> createState() => _AiSelectedProductCardState();
}

class _AiSelectedProductCardState extends State<AiSelectedProductCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final identity = widget.product?.product;
    final name = identity?.productName ?? 'Selected Product';
    final category = identity?.foodCategory ?? 'Packaged Food';
    final brand = identity?.brandName ?? identity?.packageSize ?? '';
    final subtitle = brand.isNotEmpty ? '$category • $brand' : category;

    // Badges from key findings or nutrients
    final rawBadges = <_BadgeInfo>[];
    if (widget.product != null) {
      for (final finding in widget.product!.keyFindings) {
        rawBadges.add(
          _BadgeInfo(
            label: finding.title,
            severity: finding.severity,
          ),
        );
      }
      if (rawBadges.isEmpty && widget.product!.nutritionalInterpretation != null) {
        for (final n in widget.product!.nutritionalInterpretation!.nutrients) {
          if (n.classification != null && n.classification != 'Not classifiable') {
            rawBadges.add(
              _BadgeInfo(
                label: '${n.displayName} ${n.classification}',
                severity: n.concernLevel == 'CONCERN'
                    ? 'HIGH'
                    : (n.concernLevel == 'POSITIVE' ? 'POSITIVE' : 'MODERATE'),
              ),
            );
          }
        }
      }
    }

    if (rawBadges.isEmpty) {
      rawBadges.add(const _BadgeInfo(label: 'Standard Formulation', severity: 'MODERATE'));
    }

    final visibleBadges = _isExpanded ? rawBadges : rawBadges.take(2).toList();
    final remainingCount = rawBadges.length - 2;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        padding: const EdgeInsets.all(14.0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24.0),
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [
              Color(0xFFFAF7F5),
              Color(0xFFF0EBF8),
            ],
          ),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0C000000),
              blurRadius: 16.0,
              offset: Offset(0, 6),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Left Product Thumbnail (width: 72, height: 80)
            SizedBox(
              width: 72.0,
              height: 80.0,
              child: identity?.imageUrl != null && identity!.imageUrl!.trim().isNotEmpty
                  ? Image.network(
                      identity.imageUrl!,
                      fit: BoxFit.contain,
                      errorBuilder: (_, __, ___) => _buildFallbackThumbnail(),
                    )
                  : _buildFallbackThumbnail(),
            ),

            const SizedBox(width: 14.0),

            // Right Expanded Column
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 18.0,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF141414),
                    ),
                  ),
                  const SizedBox(height: 3.0),
                  Text(
                    subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 13.0,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFF5A5560),
                    ),
                  ),
                  const SizedBox(height: 10.0),
                  // Nutrition Badges Row
                  Wrap(
                    spacing: 6.0,
                    runSpacing: 6.0,
                    crossAxisAlignment: WrapCrossAlignment.center,
                    children: [
                      ...visibleBadges.map((b) => _buildBadgePill(b)),
                      if (remainingCount > 0 && !_isExpanded)
                        GestureDetector(
                          onTap: () => setState(() => _isExpanded = true),
                          child: Container(
                            height: 26.0,
                            padding: const EdgeInsets.symmetric(horizontal: 10.0),
                            decoration: BoxDecoration(
                              color: const Color(0xFFE8E0F8),
                              borderRadius: BorderRadius.circular(14.0),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  '$remainingCount more',
                                  style: const TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 11.5,
                                    fontWeight: FontWeight.w700,
                                    color: Color(0xFF2D2346),
                                  ),
                                ),
                                const SizedBox(width: 2.0),
                                const Icon(
                                  Icons.keyboard_arrow_down_rounded,
                                  size: 15.0,
                                  color: Color(0xFF2D2346),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBadgePill(_BadgeInfo b) {
    Color bg;
    Color fg;
    IconData icon;

    switch (b.severity) {
      case 'HIGH':
        bg = const Color(0xFFFDE6E6);
        fg = const Color(0xFFC92A2A);
        icon = Icons.priority_high_rounded;
        break;
      case 'POSITIVE':
        bg = const Color(0xFFE3F5E8);
        fg = const Color(0xFF1E7E34);
        icon = Icons.check_rounded;
        break;
      case 'MODERATE':
      default:
        bg = const Color(0xFFFDEFD9);
        fg = const Color(0xFFB8621B);
        icon = Icons.warning_amber_rounded;
        break;
    }

    return Container(
      height: 26.0,
      padding: const EdgeInsets.symmetric(horizontal: 8.0),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(13.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 13.0, color: fg),
          const SizedBox(width: 4.0),
          Text(
            b.label,
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 11.5,
              fontWeight: FontWeight.w700,
              color: fg,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFallbackThumbnail() {
    return Container(
      width: 72.0,
      height: 80.0,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(16.0),
      ),
      alignment: Alignment.center,
      child: const Icon(
        Icons.fastfood_rounded,
        size: 34.0,
        color: Color(0xFFAFA7B8),
      ),
    );
  }
}

class _BadgeInfo {
  final String label;
  final String severity;

  const _BadgeInfo({required this.label, required this.severity});
}
