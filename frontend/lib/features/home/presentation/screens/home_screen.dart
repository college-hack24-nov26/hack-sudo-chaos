import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../shared/widgets/yumsure_bottom_nav_bar.dart';
import '../providers/home_provider.dart';
import '../widgets/explore_categories_section.dart';
import '../widgets/home_header.dart';
import '../widgets/recent_scans_section.dart';
import '../widgets/scan_insights_section.dart';
import '../widgets/scan_product_hero_card.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final categories = ref.watch(homeCategoriesProvider);
    final selectedTimeframe = ref.watch(selectedInsightTimeframeProvider);
    final recentScansAsync = ref.watch(recentScansProvider);
    final insightsAsync = ref.watch(scanInsightsProvider);
    final screenWidth = MediaQuery.of(context).size.width;

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F4),
      body: Stack(
        children: [
          // 1. Background Artwork: Top-Right Lavender Wave (curving screenWidth * 0.52 to 220)
          Positioned(
            top: 0,
            right: 0,
            child: CustomPaint(
              size: Size(screenWidth, 220),
              painter: const _LavenderWavePainter(),
            ),
          ),

          // 2. Background Artwork: Left Orange Glow Orb (left: -60, top: 100, 210x210)
          Positioned(
            left: -60.0,
            top: 100.0,
            width: 210.0,
            height: 210.0,
            child: IgnorePointer(
              child: Container(
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Color(0xFFFF985E),
                      Color(0xFFFFC89E),
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
            child: RefreshIndicator(
              color: AppColors.brandOrange,
              backgroundColor: Colors.white,
              onRefresh: () async {
                ref.invalidate(recentScansProvider);
                ref.invalidate(scanInsightsProvider);
              },
              child: ListView(
                padding: EdgeInsets.zero,
                children: [
                  // Section A: Brand Header (YumSure logo + 42x42 action button)
                  const HomeHeader(),
                  const SizedBox(height: 10.0),

                  // Section B: Scan Product Hero Card (204h, frosted gradient, floating 64x64 scanner button)
                  ScanProductHeroCard(
                    onScan: () => context.push(AppRoutes.scanner),
                  ),
                  // Spacing accounting for the bottom: -28 floating button
                  const SizedBox(height: 38.0),

                  // Section C: Explore Categories Section (4 cropped food photos, aspectRatio: 0.88)
                  ExploreCategoriesSection(
                    categories: categories,
                    onCategorySelected: (catId) {
                      context.push('${AppRoutes.search}?category=$catId');
                    },
                    onSeeAll: () {
                      context.push(AppRoutes.search);
                    },
                  ),
                  const SizedBox(height: 18.0),

                  // Section D: Your Scan Insights (84h editorial banner, radius 24)
                  insightsAsync.when(
                    data: (insight) => ScanInsightsSection(
                      insight: insight,
                      selectedTimeframe: selectedTimeframe,
                      onTimeframeChanged: (tf) {
                        ref.read(selectedInsightTimeframeProvider.notifier).state = tf;
                      },
                      onScanProduct: () => context.push(AppRoutes.scanner),
                      onInsightTapped: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Detailed nutritional trends will be available in future phase.'),
                            duration: Duration(seconds: 1),
                          ),
                        );
                      },
                    ),
                    loading: () => const Center(
                      child: Padding(
                        padding: EdgeInsets.all(16.0),
                        child: CircularProgressIndicator(strokeWidth: 2.0, color: AppColors.brandOrange),
                      ),
                    ),
                    error: (err, _) => ScanInsightsSection(
                      insight: null,
                      error: err,
                      selectedTimeframe: selectedTimeframe,
                      onTimeframeChanged: (tf) {
                        ref.read(selectedInsightTimeframeProvider.notifier).state = tf;
                      },
                      onScanProduct: () => context.push(AppRoutes.scanner),
                      onRetry: () => ref.refresh(scanInsightsProvider),
                    ),
                  ),
                  const SizedBox(height: 18.0),

                  // Section E: Recent Scans (offline card with retry, or continuous white card with scans)
                  recentScansAsync.when(
                    data: (scans) => RecentScansSection(
                      scans: scans,
                      onProductTapped: (barcode) {
                        context.push('/product/$barcode');
                      },
                      onSeeAll: () {
                        context.push(AppRoutes.search);
                      },
                      onScanProduct: () => context.push(AppRoutes.scanner),
                    ),
                    loading: () => const Center(
                      child: Padding(
                        padding: EdgeInsets.all(16.0),
                        child: CircularProgressIndicator(strokeWidth: 2.0, color: AppColors.brandOrange),
                      ),
                    ),
                    error: (err, _) => RecentScansSection(
                      scans: const [],
                      error: err,
                      onProductTapped: (barcode) => context.push('/product/$barcode'),
                      onScanProduct: () => context.push(AppRoutes.scanner),
                      onRetry: () => ref.refresh(recentScansProvider),
                    ),
                  ),
                  // Clearance for the floating 68dp bottom navigation bar
                  const SizedBox(height: 100.0),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: YumSureBottomNavBar(
        currentIndex: 0,
        onTabSelected: (index) {
          if (index == 1) {
            context.go(AppRoutes.search);
          } else if (index == 2) {
            context.go(AppRoutes.saved);
          }
        },
      ),
    );
  }
}

/// Top-Right Lavender Wave:
/// Curving from screenWidth * 0.52 at top down to 220 at the right edge
class _LavenderWavePainter extends CustomPainter {
  const _LavenderWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path()
      ..moveTo(size.width * 0.52, 0)
      ..quadraticBezierTo(size.width * 0.70, 130, size.width, 220)
      ..lineTo(size.width, 0)
      ..close();

    final paint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color(0xFFDDD2EC),
          Color(0xFFC7B6E2),
        ],
      ).createShader(Rect.fromLTWH(size.width * 0.52, 0, size.width * 0.48, 220));

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
