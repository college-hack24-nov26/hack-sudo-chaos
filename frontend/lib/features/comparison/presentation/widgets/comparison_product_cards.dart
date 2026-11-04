import '../../../../core/widgets/product_packet_image.dart';
import 'package:flutter/material.dart';
import '../../../product_details/data/models/product_response_model.dart';

class ComparisonProductCards extends StatelessWidget {
  final ProductDetailsResponse? productA;
  final ProductDetailsResponse? productB;
  final String basis;
  final VoidCallback onSelectProductA;
  final VoidCallback onSelectProductB;
  final VoidCallback onRemoveProductA;
  final VoidCallback onRemoveProductB;
  final VoidCallback? onBasisTap;

  const ComparisonProductCards({
    super.key,
    required this.productA,
    required this.productB,
    required this.basis,
    required this.onSelectProductA,
    required this.onSelectProductB,
    required this.onRemoveProductA,
    required this.onRemoveProductB,
    this.onBasisTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          // Row of two cards
          Row(
            children: [
              // Product A Card (Left)
              Expanded(
                child: _buildProductCard(
                  context: context,
                  slotLabel: 'Select Product A',
                  product: productA,
                  fillColor: const Color(0xFFFAF6F3),
                  onSelect: onSelectProductA,
                  onRemove: onRemoveProductA,
                  defaultIcon: Icons.fastfood_outlined,
                ),
              ),

              const SizedBox(width: 14.0),

              // Product B Card (Right)
              Expanded(
                child: _buildProductCard(
                  context: context,
                  slotLabel: 'Select Product B',
                  product: productB,
                  fillColor: const Color(0xFFF3EEF9),
                  onSelect: onSelectProductB,
                  onRemove: onRemoveProductB,
                  defaultIcon: Icons.restaurant_outlined,
                ),
              ),
            ],
          ),

          // Center Floating "VS" Circle (44x44)
          Container(
            width: 44.0,
            height: 44.0,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFEFE9F8),
                  Color(0xFFDECFF4),
                ],
              ),
              border: Border.all(color: Colors.white, width: 2.0),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x225A4382),
                  blurRadius: 12.0,
                  offset: Offset(0, 4),
                ),
              ],
            ),
            alignment: Alignment.center,
            child: const Text(
              'VS',
              style: TextStyle(
                fontFamily: 'Manrope',
                fontSize: 14.0,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.2,
                color: Color(0xFF181818),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductCard({
    required BuildContext context,
    required String slotLabel,
    required ProductDetailsResponse? product,
    required Color fillColor,
    required VoidCallback onSelect,
    required VoidCallback onRemove,
    required IconData defaultIcon,
  }) {
    return Container(
      constraints: const BoxConstraints(minHeight: 210.0),
      padding: const EdgeInsets.all(14.0),
      decoration: BoxDecoration(
        color: fillColor,
        borderRadius: BorderRadius.circular(24.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D000000),
            blurRadius: 16.0,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: product == null
          ? _buildEmptyState(slotLabel: slotLabel, onSelect: onSelect, icon: defaultIcon)
          : _buildSelectedState(product: product, onRemove: onRemove),
    );
  }

  Widget _buildEmptyState({
    required String slotLabel,
    required VoidCallback onSelect,
    required IconData icon,
  }) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 58.0,
          height: 58.0,
          decoration: BoxDecoration(
            color: Colors.white,
            shape: BoxShape.circle,
            border: Border.all(color: const Color(0xFFE8E0EB), width: 1.2),
          ),
          alignment: Alignment.center,
          child: Icon(
            icon,
            size: 26.0,
            color: const Color(0xFF887D94),
          ),
        ),
        const SizedBox(height: 12.0),
        Text(
          slotLabel,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Manrope',
            fontSize: 13.5,
            fontWeight: FontWeight.w700,
            color: Color(0xFF2C2636),
          ),
        ),
        const SizedBox(height: 12.0),
        InkWell(
          onTap: onSelect,
          borderRadius: BorderRadius.circular(16.0),
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 8.0),
            decoration: BoxDecoration(
              color: const Color(0xFFFF6B35),
              borderRadius: BorderRadius.circular(16.0),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x28FF6B35),
                  blurRadius: 8.0,
                  offset: Offset(0, 3),
                ),
              ],
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.add_rounded, size: 16.0, color: Colors.white),
                SizedBox(width: 4.0),
                Text(
                  'Add Food',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 12.0,
                    fontWeight: FontWeight.w700,
                    color: Colors.white,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSelectedState({
    required ProductDetailsResponse product,
    required VoidCallback onRemove,
  }) {
    final identity = product.product;
    final categoryText = identity.foodCategory ?? identity.brandName ?? 'Packaged Food';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        // Top row with Remove / Change button
        Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            GestureDetector(
              onTap: onRemove,
              child: Container(
                width: 26.0,
                height: 26.0,
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Color(0x14000000),
                      blurRadius: 6.0,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: const Icon(
                  Icons.close_rounded,
                  size: 15.0,
                  color: Color(0xFF181818),
                ),
              ),
            ),
          ],
        ),

        // Center Product Image (height: 92)
        ProductPacketImage(
          imageUrl: identity.imageUrl,
          barcode: identity.barcode,
          category: identity.foodCategory,
          height: 92.0,
          fit: BoxFit.contain,
        ),

        const SizedBox(height: 10.0),

        // Product Name (fontSize: 15, FontWeight.w800)
        Text(
          identity.productName,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Manrope',
            fontSize: 15.0,
            fontWeight: FontWeight.w800,
            color: Color(0xFF141414),
          ),
        ),

        const SizedBox(height: 2.0),

        // Category Subtitle (fontSize: 12, FontWeight.w400, color: #68636E)
        Text(
          categoryText,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontFamily: 'Manrope',
            fontSize: 12.0,
            fontWeight: FontWeight.w400,
            color: Color(0xFF68636E),
          ),
        ),

        const SizedBox(height: 8.0),

        // Bottom Comparison Basis Pill (height: 28, text: "100 g")
        GestureDetector(
          onTap: onBasisTap,
          child: Container(
            height: 28.0,
            padding: const EdgeInsets.symmetric(horizontal: 10.0),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14.0),
              border: Border.all(color: const Color(0xFFEAE4EC), width: 1.0),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x06000000),
                  blurRadius: 4.0,
                  offset: Offset(0, 1),
                ),
              ],
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  basis,
                  style: const TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 11.5,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF221E2A),
                  ),
                ),
                const SizedBox(width: 3.0),
                const Icon(
                  Icons.keyboard_arrow_down_rounded,
                  size: 16.0,
                  color: Color(0xFF68636E),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

}
