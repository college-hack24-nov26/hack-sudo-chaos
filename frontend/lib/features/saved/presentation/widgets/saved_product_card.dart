import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/saved_product_model.dart';

class SavedProductCard extends StatelessWidget {
  final SavedProductItem item;
  final VoidCallback onTap;
  final VoidCallback onRemoveBookmark;

  const SavedProductCard({
    super.key,
    required this.item,
    required this.onTap,
    required this.onRemoveBookmark,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF7F5),
        borderRadius: BorderRadius.circular(22.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0B000000),
            blurRadius: 10.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(22.0),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // 1. Left Product Thumbnail (62x62)
                Container(
                  width: 62.0,
                  height: 62.0,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14.0),
                    border: Border.all(color: const Color(0xFFEFE8E1), width: 0.8),
                  ),
                  alignment: Alignment.center,
                  child: (item.imageUrl != null && item.imageUrl!.isNotEmpty)
                      ? Image.network(
                          item.imageUrl!,
                          fit: BoxFit.contain,
                          errorBuilder: (_, __, ___) => const Icon(
                            Icons.inventory_2_outlined,
                            size: 26.0,
                            color: Color(0xFF8E8A93),
                          ),
                        )
                      : const Icon(
                          Icons.inventory_2_outlined,
                          size: 26.0,
                          color: Color(0xFF8E8A93),
                        ),
                ),
                const SizedBox(width: 14.0),

                // 2. Middle Expanded Column
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        item.productName,
                        style: const TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 15.5,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF141414),
                          letterSpacing: -0.2,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 3.0),
                      Text(
                        item.brandOrQuantity.isNotEmpty
                            ? '${item.category} • ${item.brandOrQuantity}'
                            : item.category,
                        style: const TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 12.5,
                          fontWeight: FontWeight.w400,
                          color: Color(0xFF68636E),
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (item.badges.isNotEmpty) ...[
                        const SizedBox(height: 8.0),
                        Wrap(
                          spacing: 8.0,
                          runSpacing: 4.0,
                          children: item.badges
                              .map((badge) => _SavedBadgeWidget(badge: badge))
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(width: 10.0),

                // 3. Right Action Row: Bookmark button + Chevron
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(
                        Icons.bookmark_rounded,
                        size: 23.0,
                        color: Color(0xFF1E1D24),
                      ),
                      padding: EdgeInsets.zero,
                      constraints: const BoxConstraints(minWidth: 32.0, minHeight: 32.0),
                      splashRadius: 20.0,
                      onPressed: onRemoveBookmark,
                    ),
                    const SizedBox(width: 4.0),
                    const Icon(
                      Icons.chevron_right_rounded,
                      size: 22.0,
                      color: Color(0xFF2C2830),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SavedBadgeWidget extends StatelessWidget {
  final SavedNutritionBadge badge;

  const _SavedBadgeWidget({required this.badge});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7.0, vertical: 2.5),
      decoration: BoxDecoration(
        color: badge.backgroundColor,
        borderRadius: BorderRadius.circular(10.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Solid Colored Circle with white icon inside
          if (badge.icon != null) ...[
            Container(
              width: 12.0,
              height: 12.0,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: badge.iconCircleColor,
              ),
              alignment: Alignment.center,
              child: Icon(
                badge.icon!,
                size: 8.0,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 4.0),
          ],
          Text(
            badge.label,
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 11.0,
              fontWeight: FontWeight.w700,
              color: badge.textColor,
            ),
          ),
        ],
      ),
    );
  }
}

