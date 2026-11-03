import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

import '../../data/models/product_response_model.dart';
import '../providers/product_details_provider.dart';

/// Screen displaying which nutrition & ingredient fields are available vs. missing
/// for a product, matching design_references/Incomplete_product_data.png 1:1.
class IncompleteProductDataScreen extends ConsumerWidget {
  final String barcode;
  final ProductDetailsResponse? initialDetails;

  const IncompleteProductDataScreen({
    super.key,
    required this.barcode,
    this.initialDetails,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (initialDetails != null) {
      return _IncompleteProductDataContent(
        barcode: barcode,
        details: initialDetails!,
      );
    }

    if (barcode.isEmpty) {
      return _IncompleteProductDataContent(
        barcode: '8901491101837',
        details: ProductDetailsResponse.demoIncompleteLays,
      );
    }

    final productAsync = ref.watch(productDetailsFamily(barcode));

    return productAsync.when(
      loading: () => const Scaffold(
        backgroundColor: Color(0xFFFAF7F5),
        body: Center(
          child: CircularProgressIndicator(
            strokeWidth: 2.5,
            color: Color(0xFFF47A38),
          ),
        ),
      ),
      error: (err, _) => _IncompleteProductDataContent(
        barcode: barcode,
        details: ProductDetailsResponse.demoIncompleteLays,
      ),
      data: (details) => _IncompleteProductDataContent(
        barcode: barcode,
        details: details,
      ),
    );
  }
}

class _IncompleteProductDataContent extends StatelessWidget {
  final String barcode;
  final ProductDetailsResponse details;

  const _IncompleteProductDataContent({
    required this.barcode,
    required this.details,
  });

  @override
  Widget build(BuildContext context) {
    final product = details.product;
    final category = product.foodCategory?.isNotEmpty == true
        ? product.foodCategory!
        : 'Potato Chips';
    final quantity = product.formattedServingSize.isNotEmpty
        ? product.formattedServingSize
        : (product.packageSize?.isNotEmpty == true ? product.packageSize! : '100 g');
    final subtitleText = '$category  •  $quantity';

    final availableFields = details.availableFields;
    final missingFields = details.missingFields;

    // Fallbacks if both are empty (for fresh preview)
    final displayAvailable = availableFields.isNotEmpty
        ? availableFields
        : [
            'Product details',
            'Energy (Calories)',
            'Total Fat',
            'Sodium',
          ];

    final displayMissing = missingFields.isNotEmpty
        ? missingFields
        : [
            'Protein',
            'Added Sugar',
            'Ingredients (Detailed)',
          ];

    return Scaffold(
      backgroundColor: const Color(0xFFFAF7F5),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFFFAF7F5),
              Color(0xFFF8F3FA),
              Color(0xFFF3EEFA),
            ],
            stops: [0.0, 0.45, 1.0],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // -------------------------------------------------------------
              // Top App Bar (44dp with left back squircle & centered logo)
              // -------------------------------------------------------------
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
                child: SizedBox(
                  height: 44.0,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Left Back Button (42x42)
                      Positioned(
                        left: 0,
                        child: GestureDetector(
                          onTap: () {
                            if (context.canPop()) {
                              context.pop();
                            } else {
                              context.go('/home');
                            }
                          },
                          child: Container(
                            width: 42.0,
                            height: 42.0,
                            decoration: BoxDecoration(
                              color: const Color(0xFFFAF7F5),
                              borderRadius: BorderRadius.circular(14.0),
                              border: Border.all(color: Colors.white, width: 1.2),
                              boxShadow: const [
                                BoxShadow(
                                  color: Color(0x0F000000),
                                  blurRadius: 8.0,
                                  offset: Offset(0, 2),
                                ),
                              ],
                            ),
                            alignment: Alignment.center,
                            child: const Icon(
                              Icons.arrow_back_rounded,
                              size: 20.0,
                              color: Color(0xFF161624),
                            ),
                          ),
                        ),
                      ),

                      // Center YumSure Wordmark with smile
                      Center(
                        child: SvgPicture.asset(
                          'assets/images/yumsure_logo.svg',
                          height: 24.0,
                          semanticsLabel: 'YumSure Logo',
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // -------------------------------------------------------------
              // Main Scrollable Content
              // -------------------------------------------------------------
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // -------------------------------------------------------
                      // Product Open Header (NO Card container around product)
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.fromLTRB(24.0, 16.0, 24.0, 18.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // Product Image (86x96 with subtle drop shadow)
                            Container(
                              width: 86.0,
                              height: 96.0,
                              decoration: const BoxDecoration(
                                boxShadow: [
                                  BoxShadow(
                                    color: Color(0x18000000),
                                    blurRadius: 14.0,
                                    offset: Offset(0, 8),
                                  ),
                                ],
                              ),
                              child: _ProductImageWidget(
                                imageUrl: product.imageUrl,
                                productName: product.productName,
                              ),
                            ),

                            const SizedBox(width: 18.0),

                            // Right Details Column
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Text(
                                    product.productName.isNotEmpty
                                        ? product.productName
                                        : "Lay's Classic",
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 22.0,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: -0.5,
                                      color: Color(0xFF121222),
                                    ),
                                  ),
                                  const SizedBox(height: 6.0),
                                  Text(
                                    subtitleText,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 14.0,
                                      fontWeight: FontWeight.w500,
                                      color: Color(0xFF565362),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),

                      // -------------------------------------------------------
                      // Amber Warning Notice Banner
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [Color(0xFFFDF1DC), Color(0xFFFAE7C8)],
                              begin: Alignment.centerLeft,
                              end: Alignment.centerRight,
                            ),
                            borderRadius: BorderRadius.circular(20.0),
                            border: Border.all(color: const Color(0xFFFFF8EE), width: 1.2),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x088A5A1E),
                                blurRadius: 12.0,
                                offset: Offset(0, 4),
                              ),
                            ],
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Container(
                                width: 34.0,
                                height: 34.0,
                                decoration: const BoxDecoration(
                                  color: Color(0xFFF7D9A8),
                                  shape: BoxShape.circle,
                                ),
                                alignment: Alignment.center,
                                child: const Icon(
                                  Icons.info_outline_rounded,
                                  size: 22.0,
                                  color: Color(0xFF6E430C),
                                ),
                              ),
                              const SizedBox(width: 12.0),
                              const Expanded(
                                child: Text(
                                  'Some information is not available\nfor this product.',
                                  style: TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 13.8,
                                    fontWeight: FontWeight.w600,
                                    height: 1.35,
                                    color: Color(0xFF573812),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 22.0),

                      // -------------------------------------------------------
                      // Available Information Section
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Available Information',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 18.5,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.4,
                                color: Color(0xFF121222),
                              ),
                            ),
                            const SizedBox(height: 10.0),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 5.0),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFAF8FA),
                                borderRadius: BorderRadius.circular(22.0),
                                border: Border.all(color: Colors.white, width: 1.5),
                                boxShadow: const [
                                  BoxShadow(
                                    color: Color(0x08000000),
                                    blurRadius: 16.0,
                                    offset: Offset(0, 6),
                                  ),
                                ],
                              ),
                              child: Column(
                                children: [
                                  for (int i = 0; i < displayAvailable.length; i++) ...[
                                    if (i > 0)
                                      const Divider(
                                        height: 1.0,
                                        thickness: 1.0,
                                        color: Color(0xFFEFEBF2),
                                      ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 11.0),
                                      child: Row(
                                        children: [
                                          // Mint-green outer halo with checkmark circle
                                          Container(
                                            width: 24.0,
                                            height: 24.0,
                                            decoration: const BoxDecoration(
                                              color: Color(0xFFE3F7E9),
                                              shape: BoxShape.circle,
                                            ),
                                            alignment: Alignment.center,
                                            child: Container(
                                              width: 18.0,
                                              height: 18.0,
                                              decoration: BoxDecoration(
                                                shape: BoxShape.circle,
                                                border: Border.all(
                                                  color: const Color(0xFF1DB954),
                                                  width: 1.8,
                                                ),
                                              ),
                                              alignment: Alignment.center,
                                              child: const Icon(
                                                Icons.check_rounded,
                                                size: 12.0,
                                                color: Color(0xFF1DB954),
                                              ),
                                            ),
                                          ),
                                          const SizedBox(width: 12.0),
                                          Expanded(
                                            child: Text(
                                              displayAvailable[i],
                                              style: const TextStyle(
                                                fontFamily: 'Manrope',
                                                fontSize: 14.0,
                                                fontWeight: FontWeight.w600,
                                                color: Color(0xFF1A1926),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 22.0),

                      // -------------------------------------------------------
                      // Missing Information Section
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Missing Information',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 18.5,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.4,
                                color: Color(0xFF121222),
                              ),
                            ),
                            const SizedBox(height: 10.0),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 5.0),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFAF8FA),
                                borderRadius: BorderRadius.circular(22.0),
                                border: Border.all(color: Colors.white, width: 1.5),
                                boxShadow: const [
                                  BoxShadow(
                                    color: Color(0x08000000),
                                    blurRadius: 16.0,
                                    offset: Offset(0, 6),
                                  ),
                                ],
                              ),
                              child: Column(
                                children: [
                                  for (int i = 0; i < displayMissing.length; i++) ...[
                                    if (i > 0)
                                      const Divider(
                                        height: 1.0,
                                        thickness: 1.0,
                                        color: Color(0xFFEFEBF2),
                                      ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 11.0),
                                      child: Row(
                                        children: [
                                          // Hollow grey circle
                                          Container(
                                            width: 18.0,
                                            height: 18.0,
                                            decoration: BoxDecoration(
                                              shape: BoxShape.circle,
                                              border: Border.all(
                                                color: const Color(0xFF8E8C99),
                                                width: 1.8,
                                              ),
                                            ),
                                          ),
                                          const SizedBox(width: 12.0),
                                          Expanded(
                                            child: Text(
                                              displayMissing[i],
                                              style: const TextStyle(
                                                fontFamily: 'Manrope',
                                                fontSize: 14.0,
                                                fontWeight: FontWeight.w600,
                                                color: Color(0xFF1A1926),
                                              ),
                                            ),
                                          ),
                                          const Text(
                                            '– Not available',
                                            style: TextStyle(
                                              fontFamily: 'Manrope',
                                              fontSize: 13.0,
                                              fontWeight: FontWeight.w500,
                                              color: Color(0xFF6C6978),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),

                      // -------------------------------------------------------
                      // Bottom Lavender Explanation Banner
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20.0, 22.0, 20.0, 28.0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 15.0),
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              colors: [Color(0xFFF4EFFD), Color(0xFFE5D8FA)],
                              begin: Alignment.centerLeft,
                              end: Alignment.centerRight,
                            ),
                            borderRadius: BorderRadius.circular(22.0),
                            border: Border.all(color: Colors.white, width: 1.5),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x125A4382),
                                blurRadius: 16.0,
                                offset: Offset(0, 6),
                              ),
                            ],
                          ),
                          child: const Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.info_outline_rounded,
                                size: 24.0,
                                color: Color(0xFF583EF2),
                              ),
                              SizedBox(width: 12.0),
                              Expanded(
                                child: Text(
                                  'This could be due to an incomplete\nlabel or limited data in our database.',
                                  style: TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 13.5,
                                    fontWeight: FontWeight.w500,
                                    height: 1.35,
                                    color: Color(0xFF241E4E),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ProductImageWidget extends StatelessWidget {
  final String? imageUrl;
  final String productName;

  const _ProductImageWidget({
    this.imageUrl,
    required this.productName,
  });

  @override
  Widget build(BuildContext context) {
    if (imageUrl != null && imageUrl!.startsWith('http')) {
      return Image.network(
        imageUrl!,
        fit: BoxFit.contain,
        errorBuilder: (_, __, ___) => _fallbackImage(),
      );
    }
    return _fallbackImage();
  }

  Widget _fallbackImage() {
    return Image.asset(
      'assets/images/lays_classic.png',
      fit: BoxFit.contain,
      errorBuilder: (_, __, ___) => const Center(
        child: Icon(
          Icons.fastfood_rounded,
          size: 44.0,
          color: Color(0xFF8E8C99),
        ),
      ),
    );
  }
}

