import 'package:flutter/material.dart';

class IngredientDisclaimerCard extends StatelessWidget {
  const IngredientDisclaimerCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        margin: const EdgeInsets.only(top: 10.0, bottom: 24.0),
        padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
        decoration: BoxDecoration(
          color: const Color(0xFFF5F2F0),
          borderRadius: BorderRadius.circular(18.0),
          border: Border.all(color: Colors.white, width: 1.2),
        ),
        child: const Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(
              Icons.info_outline_rounded,
              size: 20.0,
              color: Color(0xFF4A454E),
            ),
            SizedBox(width: 10.0),
            Expanded(
              child: Text(
                'The analysis is based on the ingredient list available on the product label. Formulation may vary by variant and region.',
                style: TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 11.8,
                  fontWeight: FontWeight.w400,
                  height: 1.35,
                  color: Color(0xFF4A454E),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
