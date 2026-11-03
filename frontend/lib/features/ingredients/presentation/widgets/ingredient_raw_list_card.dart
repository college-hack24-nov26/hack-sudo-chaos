import 'package:flutter/material.dart';

class IngredientRawListCard extends StatelessWidget {
  final String? rawText;

  const IngredientRawListCard({
    super.key,
    required this.rawText,
  });

  @override
  Widget build(BuildContext context) {
    final displayText = (rawText != null && rawText!.trim().isNotEmpty)
        ? rawText!.trim()
        : 'Ingredient list unavailable on product packaging.';

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row
          const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                'Ingredient List',
                style: TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 17.5,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.3,
                  color: Color(0xFF141414),
                ),
              ),
              Text(
                'As per product label',
                style: TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 12.5,
                  fontWeight: FontWeight.w500,
                  color: Color(0xFF3A3542),
                ),
              ),
            ],
          ),

          const SizedBox(height: 10.0),

          // Raw Ingredient Box
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 15.0),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(18.0),
              gradient: const LinearGradient(
                begin: Alignment.centerLeft,
                end: Alignment.centerRight,
                colors: [
                  Color(0xFFFAF7F5),
                  Color(0xFFF2EDF9),
                ],
              ),
              border: Border.all(color: Colors.white, width: 1.5),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x08000000),
                  blurRadius: 10.0,
                  offset: Offset(0, 3),
                ),
              ],
            ),
            child: Text(
              displayText,
              style: const TextStyle(
                fontFamily: 'Manrope',
                fontSize: 14.0,
                fontWeight: FontWeight.w500,
                color: Color(0xFF181818),
                height: 1.4,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
