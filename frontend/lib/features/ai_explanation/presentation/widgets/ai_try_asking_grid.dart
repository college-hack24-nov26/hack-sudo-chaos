import 'package:flutter/material.dart';

class AiTryAskingGrid extends StatelessWidget {
  final ValueChanged<String> onSelectQuestion;

  const AiTryAskingGrid({
    super.key,
    required this.onSelectQuestion,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Section Heading
          const Text(
            'Try asking',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 17.0,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.3,
              color: Color(0xFF141414),
            ),
          ),

          const SizedBox(height: 10.0),

          // 2x2 Pill Grid
          Column(
            children: [
              // Row 1
              Row(
                children: [
                  // Top-Left Pill (Lavender #EFEAF9)
                  Expanded(
                    child: _buildSuggestionPill(
                      text: 'Is it good for daily consumption?',
                      bgColor: const Color(0xFFEFEAF9),
                      circleColor: const Color(0xFFDED0F6),
                      icon: Icons.eco_outlined,
                      iconColor: const Color(0xFF6B4CE6),
                    ),
                  ),

                  const SizedBox(width: 8.0),

                  // Top-Right Pill (Warm Peach #FDF0E6)
                  Expanded(
                    child: _buildSuggestionPill(
                      text: 'Why is the sodium high?',
                      bgColor: const Color(0xFFFDF0E6),
                      circleColor: const Color(0xFFF9DCBA),
                      icon: Icons.view_in_ar_rounded,
                      iconColor: const Color(0xFF181818),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8.0),

              // Row 2
              Row(
                children: [
                  // Bottom-Left Pill (Soft Blue-Teal #EAF2F6)
                  Expanded(
                    child: _buildSuggestionPill(
                      text: 'Does it contain harmful additives?',
                      bgColor: const Color(0xFFEAF2F6),
                      circleColor: const Color(0xFFCCE2ED),
                      icon: Icons.science_outlined,
                      iconColor: const Color(0xFF2C6C8A),
                    ),
                  ),

                  const SizedBox(width: 8.0),

                  // Bottom-Right Pill (Soft Mint-Green #EAF6EC)
                  Expanded(
                    child: _buildSuggestionPill(
                      text: 'Is it a healthier snack option?',
                      bgColor: const Color(0xFFEAF6EC),
                      circleColor: const Color(0xFFCCEBD2),
                      icon: Icons.balance_rounded,
                      iconColor: const Color(0xFF288A42),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSuggestionPill({
    required String text,
    required Color bgColor,
    required Color circleColor,
    required IconData icon,
    required Color iconColor,
  }) {
    return GestureDetector(
      onTap: () => onSelectQuestion(text),
      child: Container(
        height: 42.0,
        padding: const EdgeInsets.symmetric(horizontal: 8.0),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(21.0),
          border: Border.all(color: Colors.white, width: 1.2),
          boxShadow: const [
            BoxShadow(
              color: Color(0x08000000),
              blurRadius: 6.0,
              offset: Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 24.0,
              height: 24.0,
              decoration: BoxDecoration(
                color: circleColor,
                shape: BoxShape.circle,
              ),
              alignment: Alignment.center,
              child: Icon(icon, size: 14.0, color: iconColor),
            ),
            const SizedBox(width: 6.0),
            Expanded(
              child: Text(
                text,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 11.2,
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF1E1B24),
                  height: 1.2,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
