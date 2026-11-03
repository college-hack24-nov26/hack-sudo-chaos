import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/search_models.dart';

class SearchCategoryPills extends StatelessWidget {
  final List<CategoryFilterItem> categories;
  final String selectedCategoryId;
  final ValueChanged<String> onCategorySelected;

  const SearchCategoryPills({
    super.key,
    required this.categories,
    required this.selectedCategoryId,
    required this.onCategorySelected,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 38.0,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8.0),
        itemBuilder: (context, index) {
          final cat = categories[index];
          final isSelected = cat.id.toLowerCase() == selectedCategoryId.toLowerCase();

          return _CategoryCapsulePill(
            item: cat,
            isSelected: isSelected,
            onTap: () => onCategorySelected(cat.id),
          );
        },
      ),
    );
  }
}

class _CategoryCapsulePill extends StatelessWidget {
  final CategoryFilterItem item;
  final bool isSelected;
  final VoidCallback onTap;

  const _CategoryCapsulePill({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor = isSelected ? const Color(0xFF1D1C24) : const Color(0xFFFAF7F5);
    final fgColor = isSelected ? Colors.white : const Color(0xFF222026);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(19.0),
        child: Container(
          height: 38.0,
          padding: const EdgeInsets.symmetric(horizontal: 14.0),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(19.0),
            border: isSelected ? null : Border.all(color: Colors.white, width: 1.2),
            boxShadow: isSelected
                ? const [
                    BoxShadow(
                      color: Color(0x221D1C24),
                      blurRadius: 10.0,
                      offset: Offset(0, 3),
                    ),
                  ]
                : const [
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
              Icon(
                item.icon,
                size: item.id == 'all' ? 15.0 : 16.0,
                color: fgColor,
              ),
              const SizedBox(width: 6.0),
              Text(
                item.label,
                style: TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: 12.5,
                  fontWeight: FontWeight.w600,
                  color: fgColor,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

