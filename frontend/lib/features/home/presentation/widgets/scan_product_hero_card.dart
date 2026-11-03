import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

/// Reconstructed Scan Product Hero Card strictly adhering to design_references/home_reference.png:
/// - Margin: horizontal 34.0
/// - Card height: 204.0, borderRadius: 30.0
/// - Frosted taupe/lavender gradient surface
/// - 1.5px white border with soft drop shadow
/// - Razor-sharp custom-painted barcode illustration (4 white brackets + 6 vertical bars)
/// - Exact typography hierarchy
/// - Floating 64x64 scan button overlapping bottom edge (bottom: -28) with gradient rim & 4-bracket viewfinder
class ScanProductHeroCard extends StatelessWidget {
  final VoidCallback onScan;

  const ScanProductHeroCard({super.key, required this.onScan});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 34.0),
      child: Stack(
        clipBehavior: Clip.none,
        alignment: Alignment.bottomCenter,
        children: [
          // 1. Hero Card Surface (204dp height, 30dp radius)
          Container(
            width: double.infinity,
            height: 204.0,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(30.0),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  const Color(0xFFC9A798).withValues(alpha: 0.85),
                  const Color(0xFF7C625E).withValues(alpha: 0.85),
                  const Color(0xFF8E86A6).withValues(alpha: 0.78),
                ],
                stops: const [0.0, 0.45, 1.0],
              ),
              border: Border.all(
                color: Colors.white.withValues(alpha: 0.65),
                width: 1.5,
              ),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x22523A34),
                  blurRadius: 24.0,
                  offset: Offset(0, 12),
                ),
              ],
            ),
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                onTap: onScan,
                borderRadius: BorderRadius.circular(30.0),
                child: Padding(
                  padding: const EdgeInsets.only(top: 22.0, left: 16.0, right: 16.0),
                  child: Column(
                    children: [
                      // Barcode Illustration (66w x 46h)
                      const CustomPaint(
                        size: Size(66.0, 46.0),
                        painter: _BarcodeIllustrationPainter(),
                      ),
                      const SizedBox(height: 12.0),
                      // Heading
                      const Text(
                        'Scan a Product',
                        style: TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 20.0,
                          fontWeight: FontWeight.w700,
                          color: Colors.white,
                          letterSpacing: -0.2,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 6.0),
                      // Subtitle
                      Text(
                        'Scan its barcode to understand\nits ingredients and nutrition.',
                        style: TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 12.5,
                          fontWeight: FontWeight.w400,
                          color: Colors.white.withValues(alpha: 0.88),
                          height: 1.35,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // 2. Floating Circular Scanner Button (64x64, bottom: -28)
          Positioned(
            bottom: -28.0,
            child: GestureDetector(
              onTap: onScan,
              child: Container(
                width: 64.0,
                height: 64.0,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomRight,
                    colors: [
                      Color(0xFFFFFFFF),
                      Color(0xFFD9BDF8),
                      Color(0xFFFF9276),
                    ],
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: Color(0x55E87A64),
                      blurRadius: 16.0,
                      offset: Offset(0, 8),
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(2.5),
                child: Container(
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        Color(0xFFFFFFFF),
                        Color(0xFFF5E6F7),
                      ],
                    ),
                  ),
                  alignment: Alignment.center,
                  child: const CustomPaint(
                    size: Size(20.0, 20.0),
                    painter: _ScannerBracketPainter(),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Razor-sharp Barcode Illustration (66w x 46h):
/// 4 white corner brackets + 6 vertical bars [2.5, 1.5, 3.0, 1.5, 2.5, 2.0]
class _BarcodeIllustrationPainter extends CustomPainter {
  const _BarcodeIllustrationPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final bracketPaint = Paint()
      ..color = Colors.white
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    const armLen = 8.0;

    // Top-Left bracket
    canvas.drawLine(const Offset(0, armLen), const Offset(0, 0), bracketPaint);
    canvas.drawLine(const Offset(0, 0), const Offset(armLen, 0), bracketPaint);

    // Top-Right bracket
    canvas.drawLine(Offset(size.width - armLen, 0), Offset(size.width, 0), bracketPaint);
    canvas.drawLine(Offset(size.width, 0), Offset(size.width, armLen), bracketPaint);

    // Bottom-Left bracket
    canvas.drawLine(Offset(0, size.height - armLen), Offset(0, size.height), bracketPaint);
    canvas.drawLine(Offset(0, size.height), Offset(armLen, size.height), bracketPaint);

    // Bottom-Right bracket
    canvas.drawLine(Offset(size.width - armLen, size.height), Offset(size.width, size.height), bracketPaint);
    canvas.drawLine(Offset(size.width, size.height), Offset(size.width, size.height - armLen), bracketPaint);

    // 6 Vertical bars: widths [2.5, 1.5, 3.0, 1.5, 2.5, 2.0]
    final barWidths = [2.5, 1.5, 3.0, 1.5, 2.5, 2.0];
    const barTop = 9.0;
    const barBottom = 37.0;
    const barHeight = barBottom - barTop;

    // Total content width calculation for center alignment
    const barSpacing = 4.8;
    double totalBarsWidth = 0.0;
    for (int i = 0; i < barWidths.length; i++) {
      totalBarsWidth += barWidths[i];
      if (i < barWidths.length - 1) totalBarsWidth += barSpacing;
    }

    double currentX = (size.width - totalBarsWidth) / 2.0;
    final barPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    for (final width in barWidths) {
      final rrect = RRect.fromRectAndRadius(
        Rect.fromLTWH(currentX, barTop, width, barHeight),
        const Radius.circular(1.0),
      );
      canvas.drawRRect(rrect, barPaint);
      currentX += width + barSpacing;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// 4 black rounded corner brackets ONLY (20x20, strokeWidth 2.2, #1E1E1E, zero center dot)
class _ScannerBracketPainter extends CustomPainter {
  const _ScannerBracketPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF1E1E1E)
      ..strokeWidth = 2.2
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    const arm = 5.5;

    // Top-Left
    canvas.drawLine(const Offset(0, arm), const Offset(0, 0), paint);
    canvas.drawLine(const Offset(0, 0), const Offset(arm, 0), paint);

    // Top-Right
    canvas.drawLine(Offset(size.width - arm, 0), Offset(size.width, 0), paint);
    canvas.drawLine(Offset(size.width, 0), Offset(size.width, arm), paint);

    // Bottom-Left
    canvas.drawLine(Offset(0, size.height - arm), Offset(0, size.height), paint);
    canvas.drawLine(Offset(0, size.height), Offset(arm, size.height), paint);

    // Bottom-Right
    canvas.drawLine(Offset(size.width - arm, size.height), Offset(size.width, size.height), paint);
    canvas.drawLine(Offset(size.width, size.height), Offset(size.width, size.height - arm), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
