import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/app_router.dart';
import '../../../../shared/widgets/yumsure_bottom_nav_bar.dart';
import '../providers/search_provider.dart';
import '../widgets/search_bar_row.dart';
import '../widgets/search_category_pills.dart';
import '../widgets/search_discovery_section.dart';
import '../widgets/search_header.dart';
import '../widgets/search_results_section.dart';

class SearchScreen extends ConsumerStatefulWidget {
  final String? initialCategory;

  const SearchScreen({super.key, this.initialCategory});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  @override
  void initState() {
    super.initState();
    if (widget.initialCategory != null && widget.initialCategory!.isNotEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        ref.read(selectedCategoryProvider.notifier).state = widget.initialCategory!;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final selectedCategory = ref.watch(selectedCategoryProvider);
    final currentQuery = ref.watch(searchQueryProvider);
    final categories = ref.watch(searchCategoriesProvider);
    final popularSearches = ref.watch(popularSearchesProvider);
    final trendingProductsAsync = ref.watch(trendingProductsProvider);
    final searchResultsAsync = ref.watch(searchResultsProvider);

    final isSearching = currentQuery.trim().isNotEmpty || (selectedCategory.toLowerCase() != 'all' && selectedCategory.isNotEmpty);

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F4),
      body: Stack(
        children: [
          // 1. Top-Right Soft Lavender Curve sweeping down right edge (width * 0.48 to 320)
          Positioned(
            top: 0,
            right: 0,
            child: CustomPaint(
              size: Size(screenWidth, 320),
              painter: const _SearchLavenderWavePainter(),
            ),
          ),

          // 2. Subtle warm peach-ivory ambient tint on the left side
          Positioned(
            left: -40.0,
            top: 80.0,
            width: 180.0,
            height: 180.0,
            child: IgnorePointer(
              child: Container(
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Color(0x35FFD5C0),
                      Color(0x10FFEADF),
                      Color(0x00FDF8F4),
                    ],
                    stops: [0.0, 0.55, 1.0],
                  ),
                ),
              ),
            ),
          ),

          // 3. Main Scrollable Content
          SafeArea(
            bottom: false,
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                const SizedBox(height: 10.0),

                // Top Branding & Title Row with 42x42 Tune Button
                SearchHeader(
                  onFilterTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Advanced nutrition filters will be available in future phase.'),
                        duration: Duration(seconds: 1),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 16.0),

                // Search Input Pill + Separate 48x48 Barcode Shortcut
                SearchBarRow(
                  initialQuery: currentQuery,
                  onQueryChanged: (q) {
                    ref.read(searchQueryProvider.notifier).state = q;
                  },
                  onBarcodeTap: () => context.push(AppRoutes.scanner),
                ),
                const SizedBox(height: 16.0),

                // 5 Category Filter Capsules (All, Snacks, Beverages, Biscuits, Dairy)
                SearchCategoryPills(
                  categories: categories,
                  selectedCategoryId: selectedCategory,
                  onCategorySelected: (catId) {
                    ref.read(selectedCategoryProvider.notifier).state = catId;
                  },
                ),
                const SizedBox(height: 22.0),

                // Discovery Sections (Popular Searches & Trending) or Search Results List
                if (!isSearching) ...[
                  SearchDiscoverySection(
                    popularSearches: popularSearches,
                    trendingProductsAsync: trendingProductsAsync,
                    onSearchTermSelected: (term) {
                      ref.read(searchQueryProvider.notifier).state = term;
                    },
                    onProductSelected: (barcode) {
                      context.push('/product/$barcode');
                    },
                    onRetryTrending: () {
                      ref.invalidate(trendingProductsProvider);
                    },
                  ),
                ] else ...[
                  SearchResultsSection(
                    searchResultsAsync: searchResultsAsync,
                    onProductTapped: (barcode) {
                      context.push('/product/$barcode');
                    },
                    onRetry: () {
                      ref.invalidate(searchResultsProvider);
                    },
                  ),
                ],

                // Clearance for floating bottom nav bar
                const SizedBox(height: 100.0),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: YumSureBottomNavBar(
        currentIndex: 1,
        onTabSelected: (index) {
          if (index == 0) {
            context.go(AppRoutes.home);
          } else if (index == 2) {
            context.go(AppRoutes.saved);
          }
        },
      ),
    );
  }
}

/// Top-Right Soft Lavender Curve sweeping down behind Header, Search Bar, and Category Pills
class _SearchLavenderWavePainter extends CustomPainter {
  const _SearchLavenderWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path()
      ..moveTo(size.width * 0.48, 0)
      ..quadraticBezierTo(size.width * 0.62, 180, size.width, 320)
      ..lineTo(size.width, 0)
      ..close();

    final paint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topRight,
        end: Alignment.bottomLeft,
        colors: [
          Color(0xFFD5C7E8),
          Color(0xFFEFE9F7),
          Color(0x00FDF8F4),
        ],
        stops: [0.0, 0.45, 1.0],
      ).createShader(Rect.fromLTWH(size.width * 0.48, 0, size.width * 0.52, 320));

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
