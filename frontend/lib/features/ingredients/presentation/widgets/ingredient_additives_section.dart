import 'package:flutter/material.dart';
import '../../data/models/ingredient_intelligence_model.dart';

class IngredientAdditivesSection extends StatelessWidget {
  final List<ParsedIngredientItem> items;

  const IngredientAdditivesSection({
    super.key,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    final additives = items.where((i) => i.isAdditive).toList();
    final hasAdditives = additives.isNotEmpty;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'Additives & Processing',
                style: TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 18.0,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.3,
                  color: Color(0xFF141414),
                ),
              ),
              // Status Badge
              if (!hasAdditives)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 5.0),
                  decoration: BoxDecoration(
                    color: const Color(0xFFE3F5E8),
                    borderRadius: BorderRadius.circular(14.0),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.check_circle_rounded,
                        size: 15.0,
                        color: Color(0xFF289E47),
                      ),
                      SizedBox(width: 5.0),
                      Text(
                        'None Declared',
                        style: TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 11.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF1E6F32),
                        ),
                      ),
                    ],
                  ),
                )
              else
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 5.0),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFFF1DE),
                    borderRadius: BorderRadius.circular(14.0),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.warning_amber_rounded,
                        size: 15.0,
                        color: Color(0xFFD97E26),
                      ),
                      const SizedBox(width: 5.0),
                      Text(
                        '${additives.length} Declared',
                        style: const TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 11.5,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFFB8621B),
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),

          const SizedBox(height: 10.0),

          // Additives Banner
          if (!hasAdditives)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 13.0),
              decoration: BoxDecoration(
                color: const Color(0xFFE9F3EC),
                borderRadius: BorderRadius.circular(18.0),
                border: Border.all(color: Colors.white, width: 1.2),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.eco_outlined,
                    size: 19.0,
                    color: Color(0xFF289E47),
                  ),
                  const SizedBox(width: 10.0),
                  Expanded(
                    child: RichText(
                      text: const TextSpan(
                        style: TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 13.5,
                          color: Color(0xFF181818),
                        ),
                        children: [
                          TextSpan(text: 'No '),
                          TextSpan(
                            text: 'food additives',
                            style: TextStyle(fontWeight: FontWeight.w700),
                          ),
                          TextSpan(text: ' (INS) are listed on the product label.'),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            )
          else
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 13.0),
              decoration: BoxDecoration(
                color: const Color(0xFFFAF7F5),
                borderRadius: BorderRadius.circular(18.0),
                border: Border.all(color: Colors.white, width: 1.2),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x08000000),
                    blurRadius: 8.0,
                    offset: Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: additives.map((add) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(
                          Icons.science_outlined,
                          size: 18.0,
                          color: Color(0xFF887D94),
                        ),
                        const SizedBox(width: 8.0),
                        Expanded(
                          child: Text(
                            '${add.name} — ${add.role}',
                            style: const TextStyle(
                              fontFamily: 'Manrope',
                              fontSize: 13.0,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF222026),
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            ),
        ],
      ),
    );
  }
}

