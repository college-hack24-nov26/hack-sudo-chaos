import 'package:flutter/material.dart';
import '../../../product_details/data/models/product_response_model.dart';

class IngredientProductSummaryCard extends StatelessWidget {
  final ProductDetailsResponse? product;

  const IngredientProductSummaryCard({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    final identity = product?.product;
    final name = identity?.productName ?? 'Product Ingredients';
    final subtitle = identity?.brandName ?? identity?.packageSize ?? 'Packaged Food Formulation';
    final category = identity?.foodCategory ?? 'Food';
    final form = identity?.foodForm.toUpperCase() ?? 'SOLID';

    final tags = <String>[category, form];
    if (identity?.isVeg == true) tags.add('100% VEGETARIAN');

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Container(
        padding: const EdgeInsets.all(16.0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(24.0),
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [
              Color(0xFFFAF7F5),
              Color(0xFFEFEAF8),
            ],
          ),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0D000000),
              blurRadius: 16.0,
              offset: Offset(0, 6),
            ),
          ],
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Left Product Image (width: 82, height: 92)
            SizedBox(
              width: 82.0,
              height: 92.0,
              child: identity?.imageUrl != null && identity!.imageUrl!.trim().isNotEmpty
                  ? Image.network(
                      identity.imageUrl!,
                      fit: BoxFit.contain,
                      errorBuilder: (_, __, ___) => _buildFallbackImage(),
                    )
                  : _buildFallbackImage(),
            ),

            const SizedBox(width: 16.0),

            // Right Expanded Column
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    name,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 22.0,
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.5,
                      color: Color(0xFF141414),
                      height: 1.2,
                    ),
                  ),
                  const SizedBox(height: 4.0),
                  Text(
                    subtitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 13.5,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFF3A3542),
                    ),
                  ),
                  const SizedBox(height: 10.0),
                  // Category Tag Pills Row
                  Wrap(
                    spacing: 8.0,
                    runSpacing: 6.0,
                    children: tags.map((tag) {
                      return Container(
                        height: 28.0,
                        padding: const EdgeInsets.symmetric(horizontal: 12.0),
                        decoration: BoxDecoration(
                          color: const Color(0xFFEDE9EE),
                          borderRadius: BorderRadius.circular(14.0),
                        ),
                        alignment: Alignment.center,
                        child: Text(
                          tag,
                          style: const TextStyle(
                            fontFamily: 'Manrope',
                            fontSize: 12.0,
                            fontWeight: FontWeight.w600,
                            color: Color(0xFF222026),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFallbackImage() {
    return Container(
      width: 82.0,
      height: 92.0,
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(16.0),
      ),
      alignment: Alignment.center,
      child: const Icon(
        Icons.inventory_2_outlined,
        size: 38.0,
        color: Color(0xFFAFA7B8),
      ),
    );
  }
}

