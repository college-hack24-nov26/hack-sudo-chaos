import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../core/widgets/product_packet_image.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/search_models.dart';

class SearchDiscoverySection extends StatefulWidget {
  final List<PopularSearchItem> popularSearches;
  final AsyncValue<List<TrendingProductItem>> trendingProductsAsync;
  final ValueChanged<String> onSearchTermSelected;
  final ValueChanged<String> onProductSelected;
  final VoidCallback onRetryTrending;

  const SearchDiscoverySection({
    super.key,
    required this.popularSearches,
    required this.trendingProductsAsync,
    required this.onSearchTermSelected,
    required this.onProductSelected,
    required this.onRetryTrending,
  });

  @override
  State<SearchDiscoverySection> createState() => _SearchDiscoverySectionState();
}

class _SearchDiscoverySectionState extends State<SearchDiscoverySection> {
  final int _activeTrendingPage = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // 1. Popular Searches Section
        _buildPopularSearchesHeader(),
        const SizedBox(height: 10.0),
        _buildPopularSearchesChips(),
        const SizedBox(height: 24.0),

        // 2. Trending Products Section
        _buildTrendingHeader(),
        const SizedBox(height: 12.0),
        _buildTrendingContent(),
      ],
    );
  }

  Widget _buildPopularSearchesHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          const Text(
            'Popular Searches',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 16.5,
              fontWeight: FontWeight.w700,
              color: Color(0xFF161616),
              letterSpacing: -0.2,
            ),
          ),
          InkWell(
            onTap: () {},
            borderRadius: BorderRadius.circular(6.0),
            child: const Padding(
              padding: EdgeInsets.symmetric(horizontal: 4.0, vertical: 2.0),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'See all',
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 12.5,
                      fontWeight: FontWeight.w500,
                      color: Color(0xFF5A5560),
                    ),
                  ),
                  SizedBox(width: 3.0),
                  Icon(Icons.arrow_forward_rounded, size: 13.0, color: Color(0xFF5A5560)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPopularSearchesChips() {
    return SizedBox(
      height: 34.0,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        itemCount: widget.popularSearches.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8.0),
        itemBuilder: (context, index) {
          final item = widget.popularSearches[index];
          return Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: () => widget.onSearchTermSelected(item.query),
              borderRadius: BorderRadius.circular(17.0),
              child: Container(
                height: 34.0,
                padding: const EdgeInsets.symmetric(horizontal: 14.0),
                decoration: BoxDecoration(
                  color: const Color(0xFFFAF7F5),
                  borderRadius: BorderRadius.circular(17.0),
                  border: Border.all(color: Colors.white, width: 1.2),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x0A000000),
                      blurRadius: 8.0,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    if (item.isHot) ...[
                      const Icon(
                        Icons.local_fire_department_rounded,
                        size: 15.0,
                        color: Color(0xFFF47A38),
                      ),
                      const SizedBox(width: 4.0),
                    ],
                    Text(
                      item.query,
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 12.5,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF222026),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildTrendingHeader() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 20.0),
      child: Text(
        'Trending Products',
        style: TextStyle(
          fontFamily: AppTypography.fontFamily,
          fontSize: 16.5,
          fontWeight: FontWeight.w700,
          color: Color(0xFF161616),
          letterSpacing: -0.2,
        ),
      ),
    );
  }

  Widget _buildTrendingContent() {
    return widget.trendingProductsAsync.when(
      data: (items) {
        if (items.isEmpty) {
          return _buildTrendingOfflineCard(
            title: 'No Trending Data',
            subtitle: 'Trending packaged food insights will appear here',
          );
        }

        return Column(
          children: [
            SizedBox(
              height: 92.0,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                itemCount: items.length,
                separatorBuilder: (_, __) => const SizedBox(width: 10.0),
                itemBuilder: (context, index) {
                  return _TrendingProductCard(
                    item: items[index],
                    onTap: () => widget.onProductSelected(items[index].barcode),
                  );
                },
              ),
            ),
            const SizedBox(height: 10.0),
            // Centered 3-dot pagination indicator
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(
                3,
                (i) => Container(
                  width: 6.0,
                  height: 6.0,
                  margin: const EdgeInsets.symmetric(horizontal: 3.0),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: i == _activeTrendingPage
                        ? const Color(0xFF2D2933)
                        : const Color(0xFFCCC6D2),
                  ),
                ),
              ),
            ),
          ],
        );
      },
      loading: () => const Padding(
        padding: EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
        child: Center(
          child: CircularProgressIndicator(strokeWidth: 2.0, color: AppColors.brandOrange),
        ),
      ),
      error: (_, __) => _buildTrendingOfflineCard(
        title: 'Trending Offline',
        subtitle: 'Connect backend to discover trending food products',
        onRetry: widget.onRetryTrending,
      ),
    );
  }

  Widget _buildTrendingOfflineCard({
    required String title,
    required String subtitle,
    VoidCallback? onRetry,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        height: 84.0,
        decoration: BoxDecoration(
          color: const Color(0xFFFFF9F6),
          borderRadius: BorderRadius.circular(24.0),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0D000000),
              blurRadius: 14.0,
              offset: Offset(0, 6),
            ),
          ],
        ),
        clipBehavior: Clip.antiAlias,
        child: Stack(
          children: [
            // Bottom-Right Soft Pink Curved Wave (#FFE5DF)
            const Positioned.fill(
              child: CustomPaint(
                painter: _TrendingWavePainter(),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: Row(
                children: [
                  Container(
                    width: 48.0,
                    height: 48.0,
                    decoration: BoxDecoration(
                      color: const Color(0xFFFDE2DA),
                      borderRadius: BorderRadius.circular(14.0),
                    ),
                    alignment: Alignment.center,
                    child: const Icon(
                      Icons.trending_up_rounded,
                      size: 24.0,
                      color: Color(0xFFF05442),
                    ),
                  ),
                  const SizedBox(width: 14.0),
                  Expanded(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          title,
                          style: const TextStyle(
                            fontFamily: AppTypography.fontFamily,
                            fontSize: 14.0,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF141414),
                          ),
                        ),
                        const SizedBox(height: 2.0),
                        Text(
                          subtitle,
                          style: const TextStyle(
                            fontFamily: AppTypography.fontFamily,
                            fontSize: 11.5,
                            color: Color(0xFF6E6877),
                            height: 1.3,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                  if (onRetry != null)
                    Material(
                      color: Colors.transparent,
                      child: InkWell(
                        onTap: onRetry,
                        borderRadius: BorderRadius.circular(17.0),
                        child: Container(
                          width: 34.0,
                          height: 34.0,
                          decoration: BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                            border: Border.all(color: const Color(0xFFEFE6DF), width: 1.0),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x0A000000),
                                blurRadius: 6.0,
                                offset: Offset(0, 2),
                              ),
                            ],
                          ),
                          alignment: Alignment.center,
                          child: const Icon(
                            Icons.refresh_rounded,
                            size: 16.0,
                            color: Color(0xFF181818),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TrendingProductCard extends StatelessWidget {
  final TrendingProductItem item;
  final VoidCallback onTap;

  const _TrendingProductCard({required this.item, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 158.0,
      height: 92.0,
      decoration: BoxDecoration(
        color: const Color(0xFFFFFDFB),
        borderRadius: BorderRadius.circular(20.0),
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
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(20.0),
          child: Stack(
            children: [
              // Bottom-Right curved wave
              const Positioned.fill(
                child: CustomPaint(
                  painter: _TrendingWavePainter(),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Row(
                  children: [
                    // Left Product Thumbnail (42x58)
                    ProductPacketImage(
                      imageUrl: item.imageUrl,
                      barcode: item.barcode,
                      category: item.category,
                      width: 42.0,
                      height: 58.0,
                      fit: BoxFit.contain,
                      borderRadius: BorderRadius.circular(10.0),
                      backgroundColor: const Color(0xFFF9F5F1),
                    ),
                    const SizedBox(width: 8.0),
                    // Right Details Column
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            item.productName,
                            style: const TextStyle(
                              fontFamily: AppTypography.fontFamily,
                              fontSize: 13.0,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF161616),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2.0),
                          Text(
                            item.category,
                            style: const TextStyle(
                              fontFamily: AppTypography.fontFamily,
                              fontSize: 11.0,
                              color: Color(0xFF78737A),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          if (item.badge != null) ...[
                            const SizedBox(height: 4.0),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 5.0, vertical: 2.0),
                              decoration: BoxDecoration(
                                color: item.badge!.backgroundColor,
                                borderRadius: BorderRadius.circular(6.0),
                              ),
                              child: Text(
                                item.badge!.label,
                                style: TextStyle(
                                  fontFamily: AppTypography.fontFamily,
                                  fontSize: 9.5,
                                  fontWeight: FontWeight.w700,
                                  color: item.badge!.textColor,
                                ),
                                maxLines: 1,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TrendingWavePainter extends CustomPainter {
  const _TrendingWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final wavePaint = Paint()
      ..color = const Color(0xFFFFE5DF).withValues(alpha: 0.6)
      ..style = PaintingStyle.fill;

    final path = Path()
      ..moveTo(size.width * 0.65, size.height)
      ..quadraticBezierTo(
        size.width * 0.80,
        size.height * 0.35,
        size.width,
        size.height * 0.25,
      )
      ..lineTo(size.width, size.height)
      ..close();

    canvas.drawPath(path, wavePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
