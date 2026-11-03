import 'package:flutter/material.dart';
import '../../data/models/comparison_models.dart';

class ComparisonNutritionTable extends StatelessWidget {
  final List<ComparisonNutrientRow> rows;
  final String basis;

  const ComparisonNutritionTable({
    super.key,
    required this.rows,
    this.basis = 'per 100 g',
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Section Heading
          RichText(
            text: TextSpan(
              style: const TextStyle(
                fontFamily: 'Manrope',
                color: Color(0xFF141414),
              ),
              children: [
                const TextSpan(
                  text: 'Nutrition Comparison ',
                  style: TextStyle(
                    fontSize: 17.0,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.3,
                  ),
                ),
                TextSpan(
                  text: '($basis)',
                  style: const TextStyle(
                    fontSize: 15.0,
                    fontWeight: FontWeight.w500,
                    color: Color(0xFF3A3540),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 12.0),

          // Unified Card Container
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
            decoration: BoxDecoration(
              color: const Color(0xFFFAF7F5),
              borderRadius: BorderRadius.circular(24.0),
              border: Border.all(color: Colors.white, width: 1.5),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x0B000000),
                  blurRadius: 14.0,
                  offset: Offset(0, 4),
                ),
              ],
            ),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: rows.length,
              separatorBuilder: (context, index) => const Padding(
                padding: EdgeInsets.symmetric(vertical: 12.0),
                child: Divider(
                  height: 1.0,
                  thickness: 1.0,
                  color: Color(0xFFF0ECE8),
                ),
              ),
              itemBuilder: (context, index) {
                final row = rows[index];
                return _buildNutrientRow(row);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNutrientRow(ComparisonNutrientRow row) {
    return Column(
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Left Column (Product A)
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    row.formattedValueA,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 14.5,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF141414),
                    ),
                  ),
                  const SizedBox(height: 6.0),
                  // Progress bar
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4.0),
                    child: Container(
                      height: 7.0,
                      color: const Color(0xFFEAE5E2),
                      child: FractionallySizedBox(
                        alignment: Alignment.centerLeft,
                        widthFactor: row.progressA,
                        child: Container(color: row.colorA),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Center Column (Icon + Label)
            SizedBox(
              width: 118.0,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    row.icon,
                    size: 18.0,
                    color: const Color(0xFF222026),
                  ),
                  const SizedBox(height: 4.0),
                  Text(
                    row.displayName,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 12.5,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF222026),
                    ),
                  ),
                ],
              ),
            ),

            // Right Column (Product B)
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    row.formattedValueB,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 14.5,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF141414),
                    ),
                  ),
                  const SizedBox(height: 6.0),
                  // Progress bar
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4.0),
                    child: Container(
                      height: 7.0,
                      color: const Color(0xFFEAE5E2),
                      child: FractionallySizedBox(
                        alignment: Alignment.centerLeft,
                        widthFactor: row.progressB,
                        child: Container(color: row.colorB),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
}

