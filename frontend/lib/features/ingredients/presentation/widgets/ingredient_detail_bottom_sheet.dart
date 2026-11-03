import 'package:flutter/material.dart';
import '../../data/models/ingredient_intelligence_model.dart';

class IngredientDetailBottomSheet extends StatelessWidget {
  final ParsedIngredientItem item;

  const IngredientDetailBottomSheet({
    super.key,
    required this.item,
  });

  static Future<void> show(BuildContext context, ParsedIngredientItem item) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => IngredientDetailBottomSheet(item: item),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20.0, 12.0, 20.0, 28.0),
      decoration: const BoxDecoration(
        color: Color(0xFFFDF8F4),
        borderRadius: BorderRadius.vertical(top: Radius.circular(28.0)),
        boxShadow: [
          BoxShadow(
            color: Color(0x24000000),
            blurRadius: 20.0,
            offset: Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag Handle
          Center(
            child: Container(
              width: 40.0,
              height: 4.5,
              margin: const EdgeInsets.only(bottom: 16.0),
              decoration: BoxDecoration(
                color: const Color(0xFFD4C8BC),
                borderRadius: BorderRadius.circular(3.0),
              ),
            ),
          ),

          // Header Row with Icon, Title, and Role
          Row(
            children: [
              Container(
                width: 54.0,
                height: 54.0,
                decoration: BoxDecoration(
                  color: const Color(0xFFF3EFEA),
                  borderRadius: BorderRadius.circular(16.0),
                  border: Border.all(color: Colors.white, width: 1.5),
                ),
                alignment: Alignment.center,
                child: Icon(item.icon, size: 28.0, color: const Color(0xFF222026)),
              ),
              const SizedBox(width: 14.0),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      item.name,
                      style: const TextStyle(
                        fontFamily: 'Manrope',
                        fontSize: 18.0,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF141414),
                      ),
                    ),
                    const SizedBox(height: 4.0),
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
              ),
            ],
          ),

          const SizedBox(height: 18.0),

          // Plain Language Function
          const Text(
            'Nutritional Role & Function',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 14.0,
              fontWeight: FontWeight.w800,
              color: Color(0xFF141414),
            ),
          ),
          const SizedBox(height: 6.0),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14.0),
              border: Border.all(color: const Color(0xFFEDE6DF)),
            ),
            child: Text(
              item.explanation,
              style: const TextStyle(
                fontFamily: 'Manrope',
                fontSize: 13.0,
                color: Color(0xFF2C2832),
                height: 1.35,
              ),
            ),
          ),

          const SizedBox(height: 14.0),

          // FSSAI Statutory Reference
          const Text(
            'Statutory Regulatory Standard',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 14.0,
              fontWeight: FontWeight.w800,
              color: Color(0xFF141414),
            ),
          ),
          const SizedBox(height: 6.0),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14.0),
              border: Border.all(color: const Color(0xFFEDE6DF)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.gavel_rounded, size: 18.0, color: Color(0xFF4A4552)),
                const SizedBox(width: 8.0),
                Expanded(
                  child: Text(
                    item.fssaiReference,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 12.0,
                      fontWeight: FontWeight.w500,
                      color: Color(0xFF4A4552),
                      height: 1.3,
                    ),
                  ),
                ),
              ],
            ),
          ),

          if (item.isAllergen) ...[
            const SizedBox(height: 14.0),
            Container(
              padding: const EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: const Color(0xFFFDE8E8),
                borderRadius: BorderRadius.circular(14.0),
                border: Border.all(color: const Color(0xFFF4A3A3)),
              ),
              child: const Row(
                children: [
                  Icon(Icons.warning_amber_rounded, size: 20.0, color: Color(0xFFD9383A)),
                  SizedBox(width: 8.0),
                  Expanded(
                    child: Text(
                      'Allergen Alert: Declared major allergen under FSSAI Schedule II.',
                      style: TextStyle(
                        fontFamily: 'Manrope',
                        fontSize: 12.0,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFFD9383A),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

