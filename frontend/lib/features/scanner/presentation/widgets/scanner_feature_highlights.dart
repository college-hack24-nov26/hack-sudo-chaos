import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class ScannerFeatureHighlights extends StatelessWidget {
  const ScannerFeatureHighlights({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // 1. Heading
        const Text(
          'Scan Barcode',
          style: TextStyle(
            fontFamily: AppTypography.fontFamily,
            fontSize: 25.0,
            fontWeight: FontWeight.w800,
            letterSpacing: -0.4,
            color: Colors.white,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 6.0),

        // 2. Subtitle
        Text(
          'Align the barcode within the frame\nto scan the product.',
          style: TextStyle(
            fontFamily: AppTypography.fontFamily,
            fontSize: 13.5,
            fontWeight: FontWeight.w400,
            height: 1.38,
            color: Colors.white.withValues(alpha: 0.85),
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 18.0),

        // 3. 3-Column Feature Row with 2 Vertical Dividers
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Column 1: Auto Detect
              Expanded(
                child: _buildFeatureItem(
                  iconWidget: const CustomPaint(
                    size: Size(20.0, 20.0),
                    painter: _BarcodeBarsIconPainter(),
                  ),
                  label: 'Auto Detect',
                ),
              ),

              // Vertical Divider 1
              Container(
                width: 1.0,
                height: 36.0,
                color: Colors.white.withValues(alpha: 0.24),
              ),

              // Column 2: Instant Result
              Expanded(
                child: _buildFeatureItem(
                  iconWidget: const Icon(
                    Icons.rocket_launch_outlined,
                    size: 20.0,
                    color: Colors.white,
                  ),
                  label: 'Instant Result',
                ),
              ),

              // Vertical Divider 2
              Container(
                width: 1.0,
                height: 36.0,
                color: Colors.white.withValues(alpha: 0.24),
              ),

              // Column 3: Reliable Info
              Expanded(
                child: _buildFeatureItem(
                  iconWidget: const Icon(
                    Icons.verified_user_outlined,
                    size: 20.0,
                    color: Colors.white,
                  ),
                  label: 'Reliable Info',
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFeatureItem({
    required Widget iconWidget,
    required String label,
  }) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // 44x44 circular frosted glass badge
        Container(
          width: 44.0,
          height: 44.0,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.16),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.35),
              width: 1.0,
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x1F000000),
                blurRadius: 8.0,
                offset: Offset(0, 3),
              ),
            ],
          ),
          alignment: Alignment.center,
          child: iconWidget,
        ),
        const SizedBox(height: 8.0),
        Text(
          label,
          style: const TextStyle(
            fontFamily: AppTypography.fontFamily,
            fontSize: 12.0,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
          textAlign: TextAlign.center,
          maxLines: 1,
        ),
      ],
    );
  }
}

/// Custom barcode bars icon painter for Auto Detect (20x20)
class _BarcodeBarsIconPainter extends CustomPainter {
  const _BarcodeBarsIconPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final barPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    const top = 3.0;
    const height = 14.0;
    final bars = [
      {'x': 2.0, 'w': 2.0},
      {'x': 6.0, 'w': 1.2},
      {'x': 9.5, 'w': 2.2},
      {'x': 13.5, 'w': 1.2},
      {'x': 16.5, 'w': 1.8},
    ];

    for (final b in bars) {
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(b['x']!, top, b['w']!, height),
          const Radius.circular(0.6),
        ),
        barPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

