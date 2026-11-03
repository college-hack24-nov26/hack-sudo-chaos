import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import '../../data/models/comparison_models.dart';
import '../../../product_details/data/models/product_response_model.dart';

class ComparisonIngredientsAllergens extends StatelessWidget {
  final ProductDetailsResponse? productA;
  final ProductDetailsResponse? productB;

  const ComparisonIngredientsAllergens({
    super.key,
    required this.productA,
    required this.productB,
  });

  @override
  Widget build(BuildContext context) {
    final nameA = productA?.product.productName ?? 'Product A';
    final nameB = productB?.product.productName ?? 'Product B';

    final ingA = ComparisonAnalysisHelper.extractIngredientsGlance(productA);
    final ingB = ComparisonAnalysisHelper.extractIngredientsGlance(productB);

    final allgA = ComparisonAnalysisHelper.extractAllergenGlance(productA);
    final allgB = ComparisonAnalysisHelper.extractAllergenGlance(productB);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Left Card (Ingredients at Glance)
          Expanded(
            child: _buildComparisonCard(
              headerIcon: Icons.eco_outlined,
              headerIconColor: const Color(0xFF379E52),
              headerTitle: 'Ingredients at Glance',
              leftPillBg: const Color(0xFFFCE4E6),
              leftTextColor: const Color(0xFF2A1E22),
              leftText: ingA,
              leftLabel: nameA,
              rightPillBg: const Color(0xFFE6E0F8),
              rightTextColor: const Color(0xFF221E2A),
              rightText: ingB,
              rightLabel: nameB,
            ),
          ),

          const SizedBox(width: 12.0),

          // Right Card (Allergen Information)
          Expanded(
            child: _buildComparisonCard(
              context: context,
              onTap: () {
                final barcode = productA?.product.barcode.isNotEmpty == true
                    ? productA!.product.barcode
                    : (productB?.product.barcode ?? '');
                if (barcode.isNotEmpty) {
                  context.push('/product/$barcode/allergens');
                }
              },
              headerIcon: Icons.shield_outlined,
              headerIconColor: const Color(0xFFE85D35),
              headerTitle: 'Allergen Information',
              leftPillBg: const Color(0xFFFCE4E6),
              leftTextColor: const Color(0xFF2A1E22),
              leftText: allgA,
              leftLabel: nameA,
              rightPillBg: const Color(0xFFFDF0D8),
              rightTextColor: const Color(0xFF2C2216),
              rightText: allgB,
              rightLabel: nameB,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildComparisonCard({
    BuildContext? context,
    VoidCallback? onTap,
    required IconData headerIcon,
    required Color headerIconColor,
    required String headerTitle,
    required Color leftPillBg,
    required Color leftTextColor,
    required String leftText,
    required String leftLabel,
    required Color rightPillBg,
    required Color rightTextColor,
    required String rightText,
    required String rightLabel,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        constraints: const BoxConstraints(minHeight: 140.0),
      padding: const EdgeInsets.all(12.0),
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
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row
          Row(
            children: [
              Icon(headerIcon, size: 18.0, color: headerIconColor),
              const SizedBox(width: 6.0),
              Expanded(
                child: Text(
                  headerTitle,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 13.0,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF141414),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 10.0),

          // Split Content Row
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Left Product Pill
              Expanded(
                child: Column(
                  children: [
                    Container(
                      width: double.infinity,
                      constraints: const BoxConstraints(minHeight: 52.0),
                      padding: const EdgeInsets.symmetric(horizontal: 6.0, vertical: 8.0),
                      decoration: BoxDecoration(
                        color: leftPillBg,
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        leftText,
                        textAlign: TextAlign.center,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 10.5,
                          fontWeight: FontWeight.w600,
                          color: leftTextColor,
                          height: 1.25,
                        ),
                      ),
                    ),
                    const SizedBox(height: 5.0),
                    Text(
                      leftLabel,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontFamily: 'Manrope',
                        fontSize: 10.5,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF5A5560),
                      ),
                    ),
                  ],
                ),
              ),

              // Vertical Divider
              Container(
                width: 1.0,
                height: 60.0,
                margin: const EdgeInsets.symmetric(horizontal: 6.0),
                color: const Color(0xFFE5E0DC),
              ),

              // Right Product Pill
              Expanded(
                child: Column(
                  children: [
                    Container(
                      width: double.infinity,
                      constraints: const BoxConstraints(minHeight: 52.0),
                      padding: const EdgeInsets.symmetric(horizontal: 6.0, vertical: 8.0),
                      decoration: BoxDecoration(
                        color: rightPillBg,
                        borderRadius: BorderRadius.circular(12.0),
                      ),
                      alignment: Alignment.center,
                      child: Text(
                        rightText,
                        textAlign: TextAlign.center,
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 10.5,
                          fontWeight: FontWeight.w600,
                          color: rightTextColor,
                          height: 1.25,
                        ),
                      ),
                    ),
                    const SizedBox(height: 5.0),
                    Text(
                      rightLabel,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontFamily: 'Manrope',
                        fontSize: 10.5,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF5A5560),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      ),
    );
  }
}
