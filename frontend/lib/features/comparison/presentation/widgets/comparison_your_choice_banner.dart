import 'package:flutter/material.dart';

class ComparisonYourChoiceBanner extends StatelessWidget {
  final String summary;

  const ComparisonYourChoiceBanner({
    super.key,
    required this.summary,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(20.0, 14.0, 20.0, 24.0),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 18.0, vertical: 16.0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24.0),
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [
              Color(0xFFF5F0FC),
              Color(0xFFDFD0F7),
            ],
          ),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x125A4382),
              blurRadius: 14.0,
              offset: Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Left Icon (Purple 4-point sparkles)
            const Icon(
              Icons.auto_awesome,
              size: 28.0,
              color: Color(0xFF7B5CE6),
            ),

            const SizedBox(width: 14.0),

            // Right Expanded Column
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Your Choice',
                    style: TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 15.5,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.2,
                      color: Color(0xFF141414),
                    ),
                  ),
                  const SizedBox(height: 3.0),
                  Text(
                    summary,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 12.5,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFF383244),
                      height: 1.35,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
