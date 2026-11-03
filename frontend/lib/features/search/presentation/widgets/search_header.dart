import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class SearchHeader extends StatelessWidget {
  final VoidCallback? onFilterTap;

  const SearchHeader({super.key, this.onFilterTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Top Bar: Exact YumSure Logo (height 26px) with orange smile on top-left
          const SizedBox(
            height: 26.0,
            child: Stack(
              clipBehavior: Clip.none,
              alignment: Alignment.centerLeft,
              children: [
                Text(
                  'YumSure',
                  style: TextStyle(
                    fontFamily: AppTypography.fontFamily,
                    fontSize: 23.0,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.6,
                    color: Color(0xFF141414),
                    height: 1.0,
                  ),
                ),
                // Curved Orange Smile centered strictly under mS junction
                Positioned(
                  left: 45.0,
                  bottom: -3.0,
                  child: CustomPaint(
                    size: Size(14.0, 5.0),
                    painter: _SearchLogoSmilePainter(),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14.0),

          // 2. Title Row: "Search" + Subtitle on Left, 42x42 Tune Button on Right
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Search',
                      style: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 28.0,
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.6,
                        color: Color(0xFF141414),
                        height: 1.1,
                      ),
                    ),
                    SizedBox(height: 4.0),
                    Text(
                      'Find, explore and compare packaged foods.',
                      style: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 13.0,
                        fontWeight: FontWeight.w400,
                        color: Color(0xFF5A5560),
                        height: 1.25,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12.0),
              // 42x42 Filter/Tune Squircle Button
              Material(
                color: Colors.transparent,
                child: InkWell(
                  onTap: onFilterTap,
                  borderRadius: BorderRadius.circular(13.0),
                  child: Container(
                    width: 42.0,
                    height: 42.0,
                    decoration: BoxDecoration(
                      color: const Color(0xFFEAE2F3),
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
                    child: const Icon(
                      Icons.tune_rounded,
                      size: 20.0,
                      color: Color(0xFF1E1E1E),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SearchLogoSmilePainter extends CustomPainter {
  const _SearchLogoSmilePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFF47A38)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.4
      ..strokeCap = StrokeCap.round;

    final path = Path()
      ..moveTo(0, 1.0)
      ..quadraticBezierTo(size.width * 0.5, size.height + 1.0, size.width, 1.0);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

