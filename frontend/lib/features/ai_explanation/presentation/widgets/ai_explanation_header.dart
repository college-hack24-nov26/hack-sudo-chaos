import 'package:flutter/material.dart';

class AiExplanationHeader extends StatelessWidget {
  const AiExplanationHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Left Sparkle Squircle (52x52)
          Container(
            width: 52.0,
            height: 52.0,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16.0),
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFF3EEFC),
                  Color(0xFFDED0F6),
                ],
              ),
              border: Border.all(color: Colors.white, width: 1.5),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x185A4382),
                  blurRadius: 12.0,
                  offset: Offset(0, 5),
                ),
              ],
            ),
            alignment: Alignment.center,
            child: const Icon(
              Icons.auto_awesome,
              size: 26.0,
              color: Color(0xFF7B5CE6),
            ),
          ),

          const SizedBox(width: 14.0),

          // Right Expanded Column
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Ask about this product',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 24.0,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.6,
                    color: Color(0xFF141414),
                    height: 1.2,
                  ),
                ),
                SizedBox(height: 4.0),
                Text(
                  'Get simple, reliable answers about its nutrition,\ningredients, claims and health impact.',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 12.8,
                    fontWeight: FontWeight.w400,
                    height: 1.35,
                    color: Color(0xFF4A4552),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
