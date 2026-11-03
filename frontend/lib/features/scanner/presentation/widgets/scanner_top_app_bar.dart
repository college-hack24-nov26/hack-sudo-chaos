import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class ScannerTopAppBar extends StatelessWidget {
  final VoidCallback onBack;
  final VoidCallback onToggleFlash;
  final VoidCallback onSwitchCamera;
  final bool isFlashActive;

  const ScannerTopAppBar({
    super.key,
    required this.onBack,
    required this.onToggleFlash,
    required this.onSwitchCamera,
    required this.isFlashActive,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      bottom: false,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
        child: SizedBox(
          height: 44.0,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // 1. Center Child: Perfectly Centered YumSure White Wordmark + Smile
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
                          fontSize: 24.0,
                          fontWeight: FontWeight.w800,
                          letterSpacing: -0.6,
                          color: Colors.white,
                          height: 1.0,
                        ),
                      ),
                      Positioned(
                        left: 47.0,
                        bottom: -3.0,
                        child: CustomPaint(
                          size: Size(14.0, 5.0),
                          painter: _ScannerLogoSmilePainter(),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // 2. Left-Aligned Child: 44x44 Frosted Back Button
              Align(
                alignment: Alignment.centerLeft,
                child: _buildFrostedButton(
                  onTap: onBack,
                  child: const Icon(
                    Icons.arrow_back_rounded,
                    size: 22.0,
                    color: Colors.white,
                  ),
                ),
              ),

              // 3. Right-Aligned Child: Row with Flashlight & Camera Buttons
              Align(
                alignment: Alignment.centerRight,
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildFrostedButton(
                      onTap: onToggleFlash,
                      isActive: isFlashActive,
                      child: Icon(
                        Icons.bolt_rounded,
                        size: 24.0,
                        color: isFlashActive ? const Color(0xFFFFD13B) : Colors.white,
                      ),
                    ),
                    const SizedBox(width: 10.0),
                    _buildFrostedButton(
                      onTap: onSwitchCamera,
                      child: const Icon(
                        Icons.camera_alt_outlined,
                        size: 21.0,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFrostedButton({
    required VoidCallback onTap,
    required Widget child,
    bool isActive = false,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14.0),
        child: Container(
          width: 44.0,
          height: 44.0,
          decoration: BoxDecoration(
            color: isActive
                ? const Color(0x66FFD13B)
                : const Color(0x452A221E),
            borderRadius: BorderRadius.circular(14.0),
            border: Border.all(
              color: isActive
                  ? const Color(0xFFFFD13B).withValues(alpha: 0.8)
                  : Colors.white.withValues(alpha: 0.32),
              width: 1.2,
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x2A000000),
                blurRadius: 8.0,
                offset: Offset(0, 3),
              ),
            ],
          ),
          alignment: Alignment.center,
          child: child,
        ),
      ),
    );
  }
}

class _ScannerLogoSmilePainter extends CustomPainter {
  const _ScannerLogoSmilePainter();

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
