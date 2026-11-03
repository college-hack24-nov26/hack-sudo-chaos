import 'package:flutter/material.dart';

class LoadingScannerSphere extends StatelessWidget {
  const LoadingScannerSphere({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer soft lavender halo circle (168x168)
          Container(
            width: 168.0,
            height: 168.0,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Color(0xFFE8DFFA),
                  Color(0x00F2ECFA),
                ],
                stops: [0.35, 1.0],
              ),
            ),
          ),

          // Inner 3D glossy sphere (132x132)
          Container(
            width: 132.0,
            height: 132.0,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFFFFFFF),
                  Color(0xFFF3EEFF),
                  Color(0xFFD2C0FF),
                ],
                stops: [0.0, 0.45, 1.0],
              ),
              border: Border.all(color: Colors.white, width: 2.0),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x266B4CE6),
                  blurRadius: 24.0,
                  offset: Offset(0, 10),
                ),
              ],
            ),
            alignment: Alignment.center,
            // Center Scanner Icon (54x48 CustomPainter)
            child: const CustomPaint(
              size: Size(54.0, 48.0),
              painter: _ScannerBracketPainter(),
            ),
          ),
        ],
      ),
    );
  }
}

class _ScannerBracketPainter extends CustomPainter {
  const _ScannerBracketPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF141426)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3.5
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final w = size.width;
    final h = size.height;
    const cornerLen = 14.0;
    const r = 8.0;

    // Top-Left Corner
    final tlPath = Path()
      ..moveTo(0, cornerLen)
      ..lineTo(0, r)
      ..arcToPoint(const Offset(r, 0), radius: const Radius.circular(r))
      ..lineTo(cornerLen, 0);
    canvas.drawPath(tlPath, paint);

    // Top-Right Corner
    final trPath = Path()
      ..moveTo(w - cornerLen, 0)
      ..lineTo(w - r, 0)
      ..arcToPoint(Offset(w, r), radius: const Radius.circular(r))
      ..lineTo(w, cornerLen);
    canvas.drawPath(trPath, paint);

    // Bottom-Left Corner
    final blPath = Path()
      ..moveTo(0, h - cornerLen)
      ..lineTo(0, h - r)
      ..arcToPoint(Offset(r, h), radius: const Radius.circular(r))
      ..lineTo(cornerLen, h);
    canvas.drawPath(blPath, paint);

    // Bottom-Right Corner
    final brPath = Path()
      ..moveTo(w - cornerLen, h)
      ..lineTo(w - r, h)
      ..arcToPoint(Offset(w, h - r), radius: const Radius.circular(r))
      ..lineTo(w, h - cornerLen);
    canvas.drawPath(brPath, paint);

    // Single horizontal rounded line in the center (width: 30, strokeWidth: 3.5)
    const lineWidth = 30.0;
    final lineStartX = (w - lineWidth) / 2;
    final lineY = h / 2;
    canvas.drawLine(
      Offset(lineStartX, lineY),
      Offset(lineStartX + lineWidth, lineY),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

