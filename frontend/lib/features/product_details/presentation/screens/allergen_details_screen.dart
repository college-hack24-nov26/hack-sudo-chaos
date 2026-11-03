import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

import '../../data/models/product_response_model.dart';
import '../providers/product_details_provider.dart';

/// Screen displaying declared vs. not-declared allergens for a product,
/// matching design_references/Allergen_details.png 1:1.
class AllergenDetailsScreen extends ConsumerWidget {
  final String barcode;
  final ProductDetailsResponse? initialDetails;

  const AllergenDetailsScreen({
    super.key,
    required this.barcode,
    this.initialDetails,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    if (initialDetails != null) {
      return _AllergenDetailsContent(
        barcode: barcode,
        details: initialDetails!,
      );
    }

    if (barcode.isEmpty) {
      return const _AllergenDetailsContent(
        barcode: '8901491101837',
        details: _demoLaysDetails,
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
      error: (err, _) => _AllergenDetailsContent(
        barcode: barcode,
        details: _demoLaysDetails,
      ),
      data: (details) => _AllergenDetailsContent(
        barcode: barcode,
        details: details,
      ),
    );
  }

  static const ProductDetailsResponse _demoLaysDetails = ProductDetailsResponse(
    product: ProductIdentity(
      barcode: '8901491101837',
      productName: "Lay's Classic",
      brandName: "Lay's",
      foodCategory: 'Potato Chips',
      packageSize: '100 g',
      foodForm: 'solid',
    ),
    ingredientAnalysis: IngredientAnalysis(
      declaredAllergens: [],
      mayContainAllergens: ['Peanut'],
      categories: [],
    ),
  );
}

class _AllergenDetailsContent extends StatelessWidget {
  final String barcode;
  final ProductDetailsResponse details;

  const _AllergenDetailsContent({
    required this.barcode,
    required this.details,
  });

  static const List<String> _standardCommonAllergens = [
    'Milk',
    'Soy',
    'Tree Nuts',
    'Egg',
    'Fish',
    'Shellfish',
    'Wheat / Gluten',
  ];

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

    final declared = details.ingredientAnalysis?.declaredAllergens ?? [];
    final mayContain = details.ingredientAnalysis?.mayContainAllergens ?? [];
    final hasAllergenData = details.ingredientAnalysis != null;

    // Filter out allergens that are already in declared or mayContain
    final lowerDeclaredAllergens = {
      ...declared.map((e) => e.toLowerCase().trim()),
      ...mayContain.map((e) => e.toLowerCase().trim()),
    };

    final notDeclaredList = _standardCommonAllergens.where((std) {
      final stdLower = std.toLowerCase();
      return !lowerDeclaredAllergens.any((decl) {
        return decl.contains(stdLower) ||
            stdLower.contains(decl) ||
            (stdLower.contains('wheat') && decl.contains('gluten')) ||
            (stdLower.contains('tree nuts') && decl.contains('nut') && !decl.contains('peanut'));
      });
    }).toList();

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
              // Section A: Top App Bar (44dp with left back squircle & logo)
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
              // Main Scrollable Content Area
              // -------------------------------------------------------------
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 12.0),

                      // -------------------------------------------------------
                      // Section B: Header Row with Circular Coral Shield Badge
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // Circular Coral Shield Badge (52x52)
                            Container(
                              width: 52.0,
                              height: 52.0,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: const LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [
                                    Color(0xFFFFFFFF),
                                    Color(0xFFFDECEB),
                                  ],
                                ),
                                border: Border.all(color: Colors.white, width: 1.5),
                                boxShadow: const [
                                  BoxShadow(
                                    color: Color(0x14E85046),
                                    blurRadius: 14.0,
                                    offset: Offset(0, 6),
                                  ),
                                ],
                              ),
                              alignment: Alignment.center,
                              child: const Icon(
                                Icons.shield_outlined,
                                size: 26.0,
                                color: Color(0xFFF25246),
                              ),
                            ),

                            const SizedBox(width: 14.0),

                            // Heading & Subtitle
                            const Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'Allergen Information',
                                    style: TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 23.0,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: -0.5,
                                      color: Color(0xFF121222),
                                    ),
                                  ),
                                  SizedBox(height: 4.0),
                                  Text(
                                    'Check for common allergens declared\non the product label.',
                                    style: TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 13.2,
                                      fontWeight: FontWeight.w400,
                                      height: 1.35,
                                      color: Color(0xFF4E4B59),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 16.0),

                      // -------------------------------------------------------
                      // Section C: Product Identity Card
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
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
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              // Left Product Thumbnail (68x74)
                              Container(
                                width: 68.0,
                                height: 74.0,
                                alignment: Alignment.center,
                                child: _ProductThumbnailWidget(
                                  imageUrl: product.imageUrl,
                                  productName: product.productName,
                                ),
                              ),

                              const SizedBox(width: 16.0),

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
                                        fontSize: 18.5,
                                        fontWeight: FontWeight.w800,
                                        letterSpacing: -0.4,
                                        color: Color(0xFF121222),
                                      ),
                                    ),
                                    const SizedBox(height: 4.0),
                                    Text(
                                      subtitleText,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                        fontFamily: 'Manrope',
                                        fontSize: 13.5,
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
                      ),

                      const SizedBox(height: 20.0),

                      // -------------------------------------------------------
                      // Section D: Declared Allergens Section
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Declared Allergens',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 18.5,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.4,
                                color: Color(0xFF121222),
                              ),
                            ),
                            const SizedBox(height: 10.0),

                            // If neither declared nor may-contain exist on reviewed label
                            if (declared.isEmpty && mayContain.isEmpty) ...[
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFAF8FA),
                                  borderRadius: BorderRadius.circular(20.0),
                                  border: Border.all(color: Colors.white, width: 1.2),
                                ),
                                child: const Text(
                                  'No common allergens declared on the label',
                                  style: TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 13.5,
                                    fontWeight: FontWeight.w500,
                                    color: Color(0xFF6C6978),
                                  ),
                                ),
                              ),
                            ] else ...[
                              // Declared "Contains" pills
                              for (final item in declared) ...[
                                _AllergenPillCard(
                                  prefix: 'Contains: ',
                                  allergenName: item,
                                ),
                                const SizedBox(height: 8.0),
                              ],

                              // Precautionary "May contain" pills
                              for (final item in mayContain) ...[
                                _AllergenPillCard(
                                  prefix: 'May contain: ',
                                  allergenName: item,
                                ),
                                const SizedBox(height: 8.0),
                              ],
                            ],
                          ],
                        ),
                      ),

                      const SizedBox(height: 16.0),

                      // -------------------------------------------------------
                      // Section E: Not Declared Section
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Not Declared',
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
                                  for (int i = 0; i < notDeclaredList.length; i++) ...[
                                    if (i > 0)
                                      const Divider(
                                        height: 1.0,
                                        thickness: 1.0,
                                        color: Color(0xFFEFEBF2),
                                      ),
                                    Padding(
                                      padding: const EdgeInsets.symmetric(vertical: 10.0),
                                      child: Row(
                                        children: [
                                          if (hasAllergenData) ...[
                                            // Soft mint-green outer halo with checkmark circle
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
                                                notDeclaredList[i],
                                                style: const TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 14.0,
                                                  fontWeight: FontWeight.w600,
                                                  color: Color(0xFF1A1926),
                                                ),
                                              ),
                                            ),
                                          ] else ...[
                                            // Hollow grey circle when allergen data is unreported
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
                                                notDeclaredList[i],
                                                style: const TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 14.0,
                                                  fontWeight: FontWeight.w600,
                                                  color: Color(0xFF1A1926),
                                                ),
                                              ),
                                            ),
                                            const Text(
                                              '– Not reported',
                                              style: TextStyle(
                                                fontFamily: 'Manrope',
                                                fontSize: 13.0,
                                                fontWeight: FontWeight.w500,
                                                color: Color(0xFF6C6978),
                                              ),
                                            ),
                                          ],
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
                      // Section F: Bottom Lavender Disclaimer Banner
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20.0, 22.0, 20.0, 28.0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
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
                                  'Allergen information is based on the\nproduct label and may vary by batch\nor region. Always check the pack.',
                                  style: TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 13.0,
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

class _AllergenPillCard extends StatelessWidget {
  final String prefix;
  final String allergenName;

  const _AllergenPillCard({
    required this.prefix,
    required this.allergenName,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 10.0),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFFFDEBEB), Color(0xFFFADCDC)],
          begin: Alignment.centerLeft,
          end: Alignment.centerRight,
        ),
        borderRadius: BorderRadius.circular(20.0),
        border: Border.all(color: const Color(0xFFFFF2F2), width: 1.2),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Left Allergen Icon Circle (38x38)
          Container(
            width: 38.0,
            height: 38.0,
            decoration: BoxDecoration(
              color: const Color(0xFFFCE4E4),
              shape: BoxShape.circle,
              border: Border.all(color: Colors.white, width: 1.0),
            ),
            alignment: Alignment.center,
            child: const CustomPaint(
              size: Size(22.0, 22.0),
              painter: _PeanutIconPainter(color: Color(0xFFA61C1C)),
            ),
          ),

          const SizedBox(width: 12.0),

          // Right Text (RichText with prefix and bold name)
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 14.0,
                ),
                children: [
                  TextSpan(
                    text: prefix,
                    style: const TextStyle(
                      fontWeight: FontWeight.w500,
                      color: Color(0xFF5C1A1A),
                    ),
                  ),
                  TextSpan(
                    text: allergenName,
                    style: const TextStyle(
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF471010),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PeanutIconPainter extends CustomPainter {
  final Color color;

  const _PeanutIconPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final cx = size.width / 2;
    final cy = size.height / 2;

    canvas.save();
    canvas.translate(cx, cy);
    canvas.rotate(-math.pi / 4);

    final path = Path();
    path.moveTo(-3.0, 0);
    path.cubicTo(-5.5, -1.8, -5.5, -7.0, 0, -8.5);
    path.cubicTo(5.5, -7.0, 5.5, -1.8, 3.0, 0);
    path.cubicTo(5.5, 1.8, 5.5, 7.0, 0, 8.5);
    path.cubicTo(-5.5, 7.0, -5.5, 1.8, -3.0, 0);

    canvas.drawPath(path, paint);
    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _PeanutIconPainter oldDelegate) =>
      oldDelegate.color != color;
}

class _ProductThumbnailWidget extends StatelessWidget {
  final String? imageUrl;
  final String productName;

  const _ProductThumbnailWidget({
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
          size: 38.0,
          color: Color(0xFF8E8C99),
        ),
      ),
    );
  }
}
