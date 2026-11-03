import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../shared/widgets/yumsure_bottom_nav_bar.dart';
import '../providers/saved_products_provider.dart';
import '../widgets/save_smartly_card.dart';
import '../widgets/saved_category_count_pills.dart';
import '../widgets/saved_header.dart';
import '../widgets/saved_product_card.dart';
import '../widgets/saved_sort_bottom_sheet.dart';
import '../widgets/saved_status_cards.dart';

class SavedProductsScreen extends ConsumerWidget {
  const SavedProductsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final screenWidth = MediaQuery.of(context).size.width;
    final selectedCategory = ref.watch(selectedSavedCategoryProvider);
    final categoryCounts = ref.watch(savedCategoryCountsProvider);
    final isSearchExpanded = ref.watch(isSavedSearchExpandedProvider);
    final searchQuery = ref.watch(savedSearchQueryProvider);
    final sortOrder = ref.watch(savedSortOrderProvider);
    final filteredSavedAsync = ref.watch(filteredSavedProductsProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F4),
      body: Stack(
        children: [
          // 1. Top-Right Soft Lavender Curve (screenWidth * 0.50 down to 300)
          Positioned(
            top: 0,
            right: 0,
            child: CustomPaint(
              size: Size(screenWidth, 300),
              painter: const _SavedLavenderWavePainter(),
            ),
          ),

          // 2. Main Scrollable Content
          SafeArea(
            bottom: false,
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                const SizedBox(height: 10.0),

                // Section A: Centered Logo & Title Header with Search/Sort Squircles
                SavedHeader(
                  isSearchExpanded: isSearchExpanded,
                  searchQuery: searchQuery,
                  onToggleSearch: () {
                    final current = ref.read(isSavedSearchExpandedProvider);
                    ref.read(isSavedSearchExpandedProvider.notifier).state = !current;
                    if (current) {
                      ref.read(savedSearchQueryProvider.notifier).state = '';
                    }
                  },
                  onOpenSortSheet: () {
                    SavedSortBottomSheet.show(
                      context,
                      currentOrder: sortOrder,
                      onOrderSelected: (order) {
                        ref.read(savedSortOrderProvider.notifier).state = order;
                      },
                    );
                  },
                  onSearchQueryChanged: (q) {
                    ref.read(savedSearchQueryProvider.notifier).state = q;
                  },
                ),
                const SizedBox(height: 16.0),

                // Section B: Category Filter Pills with Dynamic Counts
                SavedCategoryCountPills(
                  selectedCategory: selectedCategory,
                  counts: categoryCounts,
                  onCategorySelected: (catId) {
                    ref.read(selectedSavedCategoryProvider.notifier).state = catId;
                  },
                ),
                const SizedBox(height: 18.0),

                // Section C: Saved Product Cards List or Empty/Offline State
                filteredSavedAsync.when(
                  data: (items) {
                    if (items.isEmpty) {
                      return SavedEmptyCard(
                        onScanProduct: () => context.push(AppRoutes.scanner),
                      );
                    }

                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0),
                      child: Column(
                        children: [
                          for (final product in items)
                            SavedProductCard(
                              item: product,
                              onTap: () => context.push('/product/${product.barcode}'),
                              onRemoveBookmark: () {
                                ref.read(savedProductsNotifierProvider.notifier).removeProduct(product.barcode);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('Removed "${product.productName}" from Saved.'),
                                    duration: const Duration(seconds: 1),
                                  ),
                                );
                              },
                            ),
                        ],
                      ),
                    );
                  },
                  loading: () => const Padding(
                    padding: EdgeInsets.symmetric(vertical: 36.0),
                    child: Center(
                      child: CircularProgressIndicator(strokeWidth: 2.0, color: AppColors.brandOrange),
                    ),
                  ),
                  error: (_, __) => SavedOfflineCard(
                    onRetry: () => ref.read(savedProductsNotifierProvider.notifier).loadSavedProducts(),
                  ),
                ),

                const SizedBox(height: 12.0),

                // Section D: "Save smartly" Feature Card (Always visible above bottom nav)
                const SaveSmartlyCard(),

                // Clearance for floating bottom nav bar
                const SizedBox(height: 96.0),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: YumSureBottomNavBar(
        currentIndex: 2,
        onTabSelected: (index) {
          if (index == 0) {
            context.go(AppRoutes.home);
          } else if (index == 1) {
            context.go(AppRoutes.search);
          }
        },
      ),
    );
  }
}

/// Top-Right Soft Lavender Curve
class _SavedLavenderWavePainter extends CustomPainter {
  const _SavedLavenderWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path()
      ..moveTo(size.width * 0.50, 0)
      ..quadraticBezierTo(size.width * 0.65, 170, size.width, 300)
      ..lineTo(size.width, 0)
      ..close();

    final paint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topRight,
        end: Alignment.bottomLeft,
        colors: [
          Color(0xFFD8CBF0),
          Color(0xFFEFE9F8),
          Color(0x00FDF8F4),
        ],
        stops: [0.0, 0.45, 1.0],
      ).createShader(Rect.fromLTWH(size.width * 0.50, 0, size.width * 0.50, 300));

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

