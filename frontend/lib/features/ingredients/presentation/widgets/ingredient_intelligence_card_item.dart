import 'package:flutter/material.dart';
import '../../data/models/ingredient_intelligence_model.dart';
import 'ingredient_detail_bottom_sheet.dart';

class IngredientIntelligenceCardItem extends StatelessWidget {
  final ParsedIngredientItem item;

  const IngredientIntelligenceCardItem({
    super.key,
    required this.item,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF7F5),
        borderRadius: BorderRadius.circular(22.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 10.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(22.0),
          onTap: () => IngredientDetailBottomSheet.show(context, item),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Row(
              children: [
                // Left Thumbnail (68x68)
                Container(
                  width: 68.0,
                  height: 68.0,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF3EFEA),
                    borderRadius: BorderRadius.circular(16.0),
                    border: Border.all(color: Colors.white, width: 1.2),
                  ),
                  alignment: Alignment.center,
                  child: Icon(
                    item.icon,
                    size: 30.0,
                    color: const Color(0xFF222026),
                  ),
                ),

                // Middle Expanded Column
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 12.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Title + Role Badge Row
                        Wrap(
                          spacing: 8.0,
                          runSpacing: 4.0,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          children: [
                            Text(
                              item.name,
                              style: const TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 15.5,
                                fontWeight: FontWeight.w800,
                                color: Color(0xFF141414),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 3.5),
                              decoration: BoxDecoration(
                                color: const Color(0xFFEAE5FD),
                                borderRadius: BorderRadius.circular(12.0),
                              ),
                              child: Text(
                                item.role,
                                style: const TextStyle(
                                  fontFamily: 'Manrope',
                                  fontSize: 11.0,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF3B28CC),
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 5.0),
                        // Plain-Language Explanation
                        Text(
                          item.explanation,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(
                            fontFamily: 'Manrope',
                            fontSize: 12.8,
                            fontWeight: FontWeight.w400,
                            height: 1.35,
                            color: Color(0xFF2C2832),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Right Chevron
                const Icon(
                  Icons.chevron_right_rounded,
                  size: 22.0,
                  color: Color(0xFF2C2832),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
