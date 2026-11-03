import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class SavedCategoryCountPills extends StatelessWidget {
  final String selectedCategory;
  final Map<String, int> counts;
  final ValueChanged<String> onCategorySelected;

  const SavedCategoryCountPills({
    super.key,
    required this.selectedCategory,
    required this.counts,
    required this.onCategorySelected,
  });

  @override
  Widget build(BuildContext context) {
    final categories = [
      _PillData(
        id: 'all',
        label: 'All (${counts['all'] ?? 0})',
        icon: null, // No icon on All matching Saved Products.png
      ),
      _PillData(
        id: 'snacks',
        label: 'Snacks (${counts['snacks'] ?? 0})',
        icon: Icons.bakery_dining_outlined,
      ),
      _PillData(
        id: 'beverages',
        label: 'Beverages (${counts['beverages'] ?? 0})',
        icon: Icons.local_drink_outlined,
      ),
      _PillData(
        id: 'biscuits',
        label: 'Biscuits (${counts['biscuits'] ?? 0})',
        icon: Icons.cookie_outlined,
      ),
      _PillData(
        id: 'dairy',
        label: 'Dairy (${counts['dairy'] ?? 0})',
        icon: Icons.water_drop_outlined,
      ),
    ];

    return SizedBox(
      height: 40.0,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 20.0),
        itemCount: categories.length,
        separatorBuilder: (_, __) => const SizedBox(width: 10.0),
        itemBuilder: (context, index) {
          final item = categories[index];
          final isSelected = item.id.toLowerCase() == selectedCategory.toLowerCase();

          return _CategoryCountPillWidget(
            item: item,
            isSelected: isSelected,
            onTap: () => onCategorySelected(item.id),
          );
        },
      ),
    );
  }
}

class _PillData {
  final String id;
  final String label;
  final IconData? icon;

  const _PillData({required this.id, required this.label, this.icon});
}

class _CategoryCountPillWidget extends StatelessWidget {
  final _PillData item;
  final bool isSelected;
  final VoidCallback onTap;

  const _CategoryCountPillWidget({
    required this.item,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor = isSelected ? const Color(0xFF1D1C24) : const Color(0xFFFAF7F5);
    final fgColor = isSelected ? Colors.white : const Color(0xFF1E1C22);

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20.0),
        child: Container(
          height: 40.0,
          padding: const EdgeInsets.symmetric(horizontal: 16.0),
          decoration: BoxDecoration(
            color: bgColor,
            borderRadius: BorderRadius.circular(20.0),
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
              if (item.icon != null) ...[
                Icon(item.icon!, size: 16.0, color: fgColor),
                const SizedBox(width: 6.0),
              ],
              Text(
                item.label,
                style: TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: isSelected ? 13.0 : 12.5,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
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

