import 'package:flutter/material.dart';
import '../../app/theme/app_typography.dart';

class YumSureBottomNavBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTabSelected;

  const YumSureBottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTabSelected,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Container(
        height: 68.0,
        margin: const EdgeInsets.fromLTRB(20.0, 0.0, 20.0, 16.0),
        padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 6.0),
        decoration: BoxDecoration(
          color: const Color(0xFFFAF7F5),
          borderRadius: BorderRadius.circular(34.0),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x12000000),
              blurRadius: 18.0,
              offset: Offset(0, 6),
            ),
          ],
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _NavBarItem(
              icon: Icons.home_rounded,
              label: 'Home',
              isSelected: currentIndex == 0,
              onTap: () => onTabSelected(0),
            ),
            _NavBarItem(
              icon: Icons.search_rounded,
              label: 'Search',
              isSelected: currentIndex == 1,
              onTap: () => onTabSelected(1),
            ),
            _NavBarItem(
              icon: Icons.bookmark_border_rounded,
              selectedIcon: Icons.bookmark_rounded,
              label: 'Saved',
              isSelected: currentIndex == 2,
              onTap: () => onTabSelected(2),
            ),
          ],
        ),
      ),
    );
  }
}

class _NavBarItem extends StatelessWidget {
  final IconData icon;
  final IconData? selectedIcon;
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _NavBarItem({
    required this.icon,
    this.selectedIcon,
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveIcon = isSelected && selectedIcon != null ? selectedIcon! : icon;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(26.0),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 78.0,
          height: 52.0,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(26.0),
            gradient: isSelected
                ? const RadialGradient(
                    colors: [
                      Color(0xFFDED0F5),
                      Color(0x00FAF7F5),
                    ],
                    stops: [0.35, 1.0],
                  )
                : null,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                effectiveIcon,
                size: 22.0,
                color: isSelected ? const Color(0xFF201A24) : const Color(0xFF7D7784),
              ),
              const SizedBox(height: 2.0),
              Text(
                label,
                style: TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: 11.0,
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                  color: isSelected ? const Color(0xFF201A24) : const Color(0xFF7D7784),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
