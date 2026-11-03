import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_typography.dart';

class HomeHeader extends StatelessWidget {
  final VoidCallback? onExploreCategories;

  const HomeHeader({super.key, this.onExploreCategories});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // 1. YumSure Logo matching exact 1:1 reference specifications
          const _YumSureBrandWordmark(),

          // 2. Top-Right Action Button (42x42, #EAE2F3, 1.2px border, 2x2 rounded-square grid)
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onExploreCategories ?? () => context.push(AppRoutes.search),
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
                  Icons.grid_view_rounded,
                  size: 20.0,
                  color: Color(0xFF2A2433),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _YumSureBrandWordmark extends StatelessWidget {
  const _YumSureBrandWordmark();

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      height: 28.0,
      child: Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.centerLeft,
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
          // Curved Orange Smile centered strictly under mS junction
          Positioned(
            left: 49.0,
            bottom: -3.5,
            child: CustomPaint(
              size: Size(15.0, 5.5),
              painter: _SmilePainter(),
            ),
          ),
        ],
      ),
    );
  }
}

class _SmilePainter extends CustomPainter {
  const _SmilePainter();

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
