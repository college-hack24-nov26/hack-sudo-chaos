import 'dart:math' as math;
import 'package:flutter/material.dart';

class ScannerReticleView extends StatelessWidget {
  final double width;
  final double height;

  const ScannerReticleView({
    super.key,
    required this.width,
    required this.height,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: width,
      height: height,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // 1. Static Frame & 4 Glowing Outward Corner Brackets
          const Positioned.fill(
            child: CustomPaint(
              painter: _ScannerReticlePainter(),
            ),
          ),

          // 2. Horizontal Glowing Laser Line at 52% height spanning 100% width
          Positioned(
            top: height * 0.52,
            left: 0.0,
            right: 0.0,
            child: Container(
              height: 3.0,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(1.5),
                gradient: const LinearGradient(
                  begin: Alignment.centerLeft,
                  end: Alignment.centerRight,
                  colors: [
                    Color(0x80FF9E5E),
                    Color(0xFFFFFFFF),
                    Color(0x80FF9E5E),
                  ],
                  stops: [0.0, 0.50, 1.0],
                ),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0xCCFF7A29),
                    blurRadius: 16.0,
                    spreadRadius: 2.0,
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// CustomPainter rendering:
/// 1. Thin subtle white outer rounded frame (32dp radius, strokeWidth 1.0, opacity 0.35)
/// 2. 4 Outward-curving thick white corner brackets (length 42px, radius 32dp, strokeWidth 4.5)
class _ScannerReticlePainter extends CustomPainter {
  const _ScannerReticlePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Offset.zero & size;
    const radius = 32.0;
    const cornerLength = 42.0;

    // 1. Thin subtle white outer frame
    final thinWhitePaint = Paint()
      ..color = Colors.white.withValues(alpha: 0.35)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    canvas.drawRRect(
      RRect.fromRectAndRadius(rect, const Radius.circular(radius)),
      thinWhitePaint,
    );

    // 2. 4 Thick Glowing White Corners curving outward along RRect boundary
    final thickCornerPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 4.5
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    // Top-Left: Start at (rect.left, rect.top + 42) -> line to (rect.left, rect.top + 32)
    // -> arcTo(Rect.fromLTWH(rect.left, rect.top, 64, 64), pi, pi / 2, false) -> line to (rect.left + 42, rect.top)
    final tlPath = Path()
      ..moveTo(rect.left, rect.top + cornerLength)
      ..lineTo(rect.left, rect.top + radius)
      ..arcTo(
        Rect.fromLTWH(rect.left, rect.top, radius * 2, radius * 2),
        math.pi,
        math.pi / 2,
        false,
      )
      ..lineTo(rect.left + cornerLength, rect.top);
    canvas.drawPath(tlPath, thickCornerPaint);

    // Top-Right: Start at (rect.right - 42, rect.top) -> line to (rect.right - 32, rect.top)
    // -> arcTo(Rect.fromLTWH(rect.right - 64, rect.top, 64, 64), -pi / 2, pi / 2, false) -> line to (rect.right, rect.top + 42)
    final trPath = Path()
      ..moveTo(rect.right - cornerLength, rect.top)
      ..lineTo(rect.right - radius, rect.top)
      ..arcTo(
        Rect.fromLTWH(rect.right - radius * 2, rect.top, radius * 2, radius * 2),
        -math.pi / 2,
        math.pi / 2,
        false,
      )
      ..lineTo(rect.right, rect.top + cornerLength);
    canvas.drawPath(trPath, thickCornerPaint);

    // Bottom-Right: Start at (rect.right, rect.bottom - 42) -> line to (rect.right, rect.bottom - 32)
    // -> arcTo(Rect.fromLTWH(rect.right - 64, rect.bottom - 64, 64, 64), 0, pi / 2, false) -> line to (rect.right - 42, rect.bottom)
    final brPath = Path()
      ..moveTo(rect.right, rect.bottom - cornerLength)
      ..lineTo(rect.right, rect.bottom - radius)
      ..arcTo(
        Rect.fromLTWH(rect.right - radius * 2, rect.bottom - radius * 2, radius * 2, radius * 2),
        0,
        math.pi / 2,
        false,
      )
      ..lineTo(rect.right - cornerLength, rect.bottom);
    canvas.drawPath(brPath, thickCornerPaint);

    // Bottom-Left: Start at (rect.left + 42, rect.bottom) -> line to (rect.left + 32, rect.bottom)
    // -> arcTo(Rect.fromLTWH(rect.left, rect.bottom - 64, 64, 64), pi / 2, pi / 2, false) -> line to (rect.left, rect.bottom - 42)
    final blPath = Path()
      ..moveTo(rect.left + cornerLength, rect.bottom)
      ..lineTo(rect.left + radius, rect.bottom)
      ..arcTo(
        Rect.fromLTWH(rect.left, rect.bottom - radius * 2, radius * 2, radius * 2),
        math.pi / 2,
        math.pi / 2,
        false,
      )
      ..lineTo(rect.left, rect.bottom - cornerLength);
    canvas.drawPath(blPath, thickCornerPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
