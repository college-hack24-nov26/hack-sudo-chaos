import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class SavedHeader extends StatelessWidget {
  final bool isSearchExpanded;
  final String searchQuery;
  final VoidCallback onToggleSearch;
  final VoidCallback onOpenSortSheet;
  final ValueChanged<String> onSearchQueryChanged;

  const SavedHeader({
    super.key,
    required this.isSearchExpanded,
    required this.searchQuery,
    required this.onToggleSearch,
    required this.onOpenSortSheet,
    required this.onSearchQueryChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Centered Top Branding Row
          const Center(
            child: SizedBox(
              height: 28.0,
              child: Stack(
                clipBehavior: Clip.none,
                alignment: Alignment.center,
                children: [
                  Text(
                    'YumSure',
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 25.0,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.6,
                      color: Color(0xFF141414),
                      height: 1.0,
                    ),
                  ),
                  Positioned(
                    left: 49.0,
                    bottom: -3.5,
                    child: CustomPaint(
                      size: Size(15.0, 5.5),
                      painter: _SavedLogoSmilePainter(),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16.0),

          // 2. Heading & Action Buttons Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Left Title + Subtitle
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Saved Products',
                      style: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 26.0,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.6,
                        color: Color(0xFF141414),
                        height: 1.1,
                      ),
                    ),
                    SizedBox(height: 4.0),
                    Text(
                      'Your collection of scanned and favourite products.',
                      style: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 12.8,
                        fontWeight: FontWeight.w400,
                        color: Color(0xFF5A5560),
                        height: 1.25,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10.0),

              // Right Action Squircles
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // 1. Search Toggle Squircle (42x42)
                  _buildActionSquircle(
                    icon: Icons.search_rounded,
                    iconSize: 21.0,
                    isActive: isSearchExpanded,
                    onTap: onToggleSearch,
                  ),
                  const SizedBox(width: 10.0),

                  // 2. Filter / Sort Squircle (42x42)
                  _buildActionSquircle(
                    icon: Icons.tune_rounded,
                    iconSize: 20.0,
                    onTap: onOpenSortSheet,
                  ),
                ],
              ),
            ],
          ),

          // 3. Smooth Expandable Local Search Bar
          if (isSearchExpanded) ...[
            const SizedBox(height: 14.0),
            Container(
              height: 44.0,
              decoration: BoxDecoration(
                color: const Color(0xFFFAF7F5),
                borderRadius: BorderRadius.circular(22.0),
                border: Border.all(color: Colors.white, width: 1.5),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x0E000000),
                    blurRadius: 10.0,
                    offset: Offset(0, 3),
                  ),
                ],
              ),
              padding: const EdgeInsets.symmetric(horizontal: 14.0),
              child: Row(
                children: [
                  const Icon(
                    Icons.search_rounded,
                    size: 20.0,
                    color: Color(0xFF6E6877),
                  ),
                  const SizedBox(width: 8.0),
                  Expanded(
                    child: TextField(
                      autofocus: true,
                      onChanged: onSearchQueryChanged,
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 13.0,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF141414),
                      ),
                      decoration: const InputDecoration(
                        hintText: 'Search saved products...',
                        hintStyle: TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 13.0,
                          fontWeight: FontWeight.w400,
                          color: Color(0xFF8E8896),
                        ),
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                  ),
                  if (searchQuery.isNotEmpty)
                    GestureDetector(
                      onTap: () => onSearchQueryChanged(''),
                      child: const Icon(
                        Icons.close_rounded,
                        size: 18.0,
                        color: Color(0xFF8E8896),
                      ),
                    ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildActionSquircle({
    required IconData icon,
    required double iconSize,
    required VoidCallback onTap,
    bool isActive = false,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(13.0),
        child: Container(
          width: 42.0,
          height: 42.0,
          decoration: BoxDecoration(
            color: isActive ? const Color(0xFFDDD2EC) : const Color(0xFFEDE6F6),
            borderRadius: BorderRadius.circular(13.0),
            border: Border.all(color: Colors.white, width: 1.2),
            boxShadow: const [
              BoxShadow(
                color: Color(0x185A4382),
                blurRadius: 10.0,
                offset: Offset(0, 4),
              ),
            ],
          ),
          alignment: Alignment.center,
          child: Icon(
            icon,
            size: iconSize,
            color: const Color(0xFF1E1E1E),
          ),
        ),
      ),
    );
  }
}

class _SavedLogoSmilePainter extends CustomPainter {
  const _SavedLogoSmilePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFF47A38)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.5
      ..strokeCap = StrokeCap.round;

    final path = Path()
      ..moveTo(0, 1.0)
      ..quadraticBezierTo(size.width * 0.5, size.height + 1.0, size.width, 1.0);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

