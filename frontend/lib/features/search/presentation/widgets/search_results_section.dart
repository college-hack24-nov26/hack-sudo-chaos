import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/search_models.dart';

class SearchResultsSection extends StatelessWidget {
  final AsyncValue<List<SearchResultItem>> searchResultsAsync;
  final ValueChanged<String> onProductTapped;
  final VoidCallback onRetry;

  const SearchResultsSection({
    super.key,
    required this.searchResultsAsync,
    required this.onProductTapped,
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: searchResultsAsync.when(
        data: (results) {
          if (results.isEmpty) {
            return _buildEmptyState();
          }

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Row
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Text(
                    'Search Results',
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 16.5,
                      fontWeight: FontWeight.w700,
                      color: Color(0xFF161616),
                      letterSpacing: -0.2,
                    ),
                  ),
                  Text(
                    '${results.length} ${results.length == 1 ? 'result' : 'results'}',
                    style: const TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 12.5,
                      fontWeight: FontWeight.w500,
                      color: Color(0xFF6E6875),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12.0),

              // Results List
              for (final item in results)
                _SearchResultCard(
                  item: item,
                  onTap: () => onProductTapped(item.barcode),
                ),
            ],
          );
        },
        loading: () => const Padding(
          padding: EdgeInsets.symmetric(vertical: 32.0),
          child: Center(
            child: CircularProgressIndicator(strokeWidth: 2.0, color: AppColors.brandOrange),
          ),
        ),
        error: (err, _) => _buildErrorCard(onRetry),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 24.0),
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
      child: const Column(
        children: [
          Icon(Icons.search_off_rounded, size: 36.0, color: Color(0xFF8E8A93)),
          SizedBox(height: 8.0),
          Text(
            'No matching products',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 14.5,
              fontWeight: FontWeight.w700,
              color: Color(0xFF141414),
            ),
          ),
          SizedBox(height: 4.0),
          Text(
            'Try searching for another food item, brand or ingredient.',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 11.5,
              color: Color(0xFF6E6877),
              height: 1.35,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard(VoidCallback onRetry) {
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
              'Search offline (backend unreachable)',
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

class _SearchResultCard extends StatelessWidget {
  final SearchResultItem item;
  final VoidCallback onTap;

  const _SearchResultCard({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF7F5),
        borderRadius: BorderRadius.circular(20.0),
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
          borderRadius: BorderRadius.circular(20.0),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Left Image (52x52, radius 12)
                Container(
                  width: 52.0,
                  height: 52.0,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12.0),
                    border: Border.all(color: const Color(0xFFEDE6DF), width: 0.8),
                  ),
                  alignment: Alignment.center,
                  child: (item.imageUrl != null && item.imageUrl!.isNotEmpty)
                      ? Image.network(
                          item.imageUrl!,
                          fit: BoxFit.contain,
                          errorBuilder: (_, __, ___) => const Icon(
                            Icons.inventory_2_outlined,
                            size: 24.0,
                            color: Color(0xFF8E8A93),
                          ),
                        )
                      : const Icon(
                          Icons.inventory_2_outlined,
                          size: 24.0,
                          color: Color(0xFF8E8A93),
                        ),
                ),
                const SizedBox(width: 12.0),

                // Middle Expanded Column
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        item.productName,
                        style: const TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 14.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF161616),
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2.0),
                      Text(
                        item.subtitleFormatted,
                        style: const TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 12.0,
                          fontWeight: FontWeight.w400,
                          color: Color(0xFF6E6875),
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      if (item.badges.isNotEmpty) ...[
                        const SizedBox(height: 6.0),
                        Wrap(
                          spacing: 6.0,
                          runSpacing: 4.0,
                          children: item.badges
                              .map((badge) => _NutritionBadgeWidget(badge: badge))
                              .toList(),
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(width: 8.0),

                // Right Chevron
                const Icon(
                  Icons.chevron_right_rounded,
                  color: Color(0xFF3A3540),
                  size: 20.0,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _NutritionBadgeWidget extends StatelessWidget {
  final NutritionBadgeItem badge;

  const _NutritionBadgeWidget({required this.badge});

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
          if (badge.icon != null) ...[
            Icon(badge.icon!, size: 11.0, color: badge.textColor),
            const SizedBox(width: 3.5),
          ],
          Text(
            badge.label,
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 11.0,
              fontWeight: FontWeight.w600,
              color: badge.textColor,
            ),
          ),
        ],
      ),
    );
  }
}
