import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class SaveSmartlyCard extends StatelessWidget {
  const SaveSmartlyCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(20.0, 8.0, 20.0, 16.0),
      padding: const EdgeInsets.symmetric(horizontal: 18.0, vertical: 16.0),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24.0),
        gradient: const LinearGradient(
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
          colors: [
            Color(0xFFF5F0FC), // Luminous lavender-ivory left
            Color(0xFFE2D4F8), // Soft lavender right
          ],
        ),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x125A4382),
            blurRadius: 16.0,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // 1. Left Sparkles Icon (Icons.auto_awesome, size 26, #8C6FE6)
          const Icon(
            Icons.auto_awesome,
            size: 26.0,
            color: Color(0xFF8C6FE6),
          ),
          const SizedBox(width: 14.0),

          // 2. Middle Text Column
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Save smartly',
                  style: TextStyle(
                    fontFamily: AppTypography.fontFamily,
                    fontSize: 15.5,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF141414),
                    letterSpacing: -0.2,
                  ),
                ),
                SizedBox(height: 3.0),
                Text(
                  'Bookmark products to quickly compare\nand revisit their nutrition insights.',
                  style: TextStyle(
                    fontFamily: AppTypography.fontFamily,
                    fontSize: 12.2,
                    fontWeight: FontWeight.w400,
                    height: 1.35,
                    color: Color(0xFF3A3542),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 12.0),

          // 3. Right 3D Glossy Bookmark Badge (54x54)
          Container(
            width: 54.0,
            height: 54.0,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16.0),
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFB9A3EC), // Glossy lilac-lavender
                  Color(0xFF9F86E0), // Rich violet
                ],
              ),
              border: Border.all(
                color: Colors.white.withValues(alpha: 0.75),
                width: 1.5,
              ),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF8C6FE6).withValues(alpha: 0.35),
                  blurRadius: 12.0,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            alignment: Alignment.center,
            child: const Icon(
              Icons.bookmark_rounded,
              size: 26.0,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }
}

