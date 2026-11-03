import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';
import '../../../../shared/widgets/yumsure_bottom_nav_bar.dart';

class SearchPlaceholderScreen extends StatelessWidget {
  const SearchPlaceholderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Search', style: AppTypography.h3),
        centerTitle: true,
      ),
      body: const Center(
        child: Padding(
          padding: EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.search_rounded, size: 48.0, color: AppColors.textTertiary),
              SizedBox(height: 16.0),
              Text('Search Screen Integration Point', style: AppTypography.h2),
              SizedBox(height: 8.0),
              Text(
                'Prepared for future Phase. Category filters and query routing are established.',
                style: AppTypography.bodyMedium,
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
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
