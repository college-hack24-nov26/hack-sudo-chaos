import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/home_models.dart';

class ExploreCategoriesSection extends StatelessWidget {
  final List<CategoryItem> categories;
  final ValueChanged<String> onCategorySelected;
  final VoidCallback? onSeeAll;

  const ExploreCategoriesSection({
    super.key,
    required this.categories,
    required this.onCategorySelected,
    this.onSeeAll,
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
                'Explore Categories',
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

        // 4 Category Cards Row (aspectRatio: 0.88, 10px spacing)
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Row(
            children: [
              for (int i = 0; i < categories.length; i++) ...[
                if (i > 0) const SizedBox(width: 10.0),
                Expanded(
                  child: AspectRatio(
                    aspectRatio: 0.88,
                    child: _CategoryCard(
                      category: categories[i],
                      onTap: () => onCategorySelected(categories[i].id),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _CategoryCard extends StatelessWidget {
  final CategoryItem category;
  final VoidCallback onTap;

  const _CategoryCard({
    required this.category,
    required this.onTap,
  });

  Color _getVignetteColor(String id) {
    switch (id) {
      case 'snacks':
        return const Color(0xD96E4726);
      case 'beverages':
        return const Color(0xE61F0D09);
      case 'biscuits':
        return const Color(0xD95C3A1E);
      case 'dairy':
        return const Color(0xCC7D756C);
      default:
        return const Color(0xD9000000);
    }
  }

  @override
  Widget build(BuildContext context) {
    final vignetteColor = _getVignetteColor(category.id);

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20.0),
        border: Border.all(color: Colors.white, width: 1.0),
        boxShadow: const [
          BoxShadow(
            color: Color(0x10000000),
            blurRadius: 10.0,
            offset: Offset(0, 4),
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
            fit: StackFit.expand,
            children: [
              // 1. Studio Photograph Crop
              if (category.assetImagePath != null)
                Image.asset(
                  category.assetImagePath!,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _buildFallbackGradient(),
                )
              else
                _buildFallbackGradient(),

              // 2. Warm Color-matched Bottom Gradient Overlay
              DecoratedBox(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Colors.transparent,
                      Colors.transparent,
                      vignetteColor,
                    ],
                    stops: const [0.0, 0.40, 1.0],
                  ),
                ),
              ),

              // 3. Category Label (bottom: 9, 12.5sp, w600)
              Positioned(
                bottom: 9.0,
                left: 2.0,
                right: 2.0,
                child: Text(
                  category.title,
                  style: const TextStyle(
                    fontFamily: AppTypography.fontFamily,
                    fontSize: 12.5,
                    fontWeight: FontWeight.w600,
                    color: Colors.white,
                    letterSpacing: 0.1,
                  ),
                  textAlign: TextAlign.center,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFallbackGradient() {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: category.gradientColors,
        ),
      ),
      child: Center(
        child: Icon(category.icon, size: 28.0, color: Colors.white),
      ),
    );
  }
}
