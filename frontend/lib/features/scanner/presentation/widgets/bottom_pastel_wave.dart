import 'package:flutter/material.dart';

class BottomPastelWave extends StatelessWidget {
  const BottomPastelWave({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 115.0,
      width: double.infinity,
      child: const CustomPaint(
        painter: _PastelWavePainter(),
      ),
    );
  }
}

class _PastelWavePainter extends CustomPainter {
  const _PastelWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    // Background wave 1 (Soft warm lavender)
    final path1 = Path();
    path1.moveTo(0, h * 0.45);
    path1.cubicTo(w * 0.25, h * 0.15, w * 0.65, h * 0.70, w, h * 0.25);
    path1.lineTo(w, h);
    path1.lineTo(0, h);
    path1.close();

    final paint1 = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          Color(0x55E8DDF8),
          Color(0x99DECFF6),
        ],
      ).createShader(Rect.fromLTWH(0, 0, w, h));
    canvas.drawPath(path1, paint1);

    // Foreground wave 2 (Soft lilac/ivory blend)
    final path2 = Path();
    path2.moveTo(0, h * 0.65);
    path2.cubicTo(w * 0.35, h * 0.85, w * 0.70, h * 0.40, w, h * 0.55);
    path2.lineTo(w, h);
    path2.lineTo(0, h);
    path2.close();

    final paint2 = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Color(0x77EFE9FA),
          Color(0xCCDECFF6),
        ],
      ).createShader(Rect.fromLTWH(0, 0, w, h));
    canvas.drawPath(path2, paint2);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

