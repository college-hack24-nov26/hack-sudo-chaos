import 'package:flutter/material.dart';

class IngredientOverallInsightCard extends StatelessWidget {
  final String insightText;

  const IngredientOverallInsightCard({
    super.key,
    required this.insightText,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        margin: const EdgeInsets.only(top: 4.0, bottom: 18.0),
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 15.0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(22.0),
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [
              Color(0xFFF3EEFA),
              Color(0xFFE8DDF8),
            ],
          ),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x105A4382),
              blurRadius: 12.0,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Left Side
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 28.0,
                  height: 28.0,
                  decoration: const BoxDecoration(
                    color: Color(0xFFD5C8F5),
                    shape: BoxShape.circle,
                  ),
                  alignment: Alignment.center,
                  child: const Text(
                    'i',
                    style: TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 15.0,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF2C1E66),
                    ),
                  ),
                ),
                const SizedBox(width: 10.0),
                const Text(
                  'Overall Insight',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 15.5,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.3,
                    color: Color(0xFF141414),
                  ),
                ),
              ],
            ),

            // Center Divider
            Container(
              width: 1.0,
              height: 36.0,
              color: const Color(0xFFCBC2DC),
              margin: const EdgeInsets.symmetric(horizontal: 14.0),
            ),

            // Right Side
            Expanded(
              child: Text(
                insightText,
                style: const TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 12.5,
                  fontWeight: FontWeight.w500,
                  height: 1.35,
                  color: Color(0xFF221E2A),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
