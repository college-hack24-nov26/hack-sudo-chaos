import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../product_details/data/models/product_response_model.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../providers/comparison_provider.dart';
import '../widgets/comparison_ingredients_allergens.dart';
import '../widgets/comparison_key_takeaways.dart';
import '../widgets/comparison_nutrition_table.dart';
import '../widgets/comparison_product_cards.dart';
import '../widgets/comparison_top_bar.dart';
import '../widgets/comparison_your_choice_banner.dart';
import '../widgets/product_picker_modal.dart';

class ProductComparisonScreen extends ConsumerStatefulWidget {
  final String? initialProductABarcode;
  final String? initialProductBBarcode;

  const ProductComparisonScreen({
    super.key,
    this.initialProductABarcode,
    this.initialProductBBarcode,
  });

  @override
  ConsumerState<ProductComparisonScreen> createState() => _ProductComparisonScreenState();
}

class _ProductComparisonScreenState extends ConsumerState<ProductComparisonScreen> {
  bool _isLoadingInitial = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadInitialBarcodes();
    });
  }

  Future<void> _loadInitialBarcodes() async {
    final barcodeA = widget.initialProductABarcode;
    final barcodeB = widget.initialProductBBarcode;

    if (barcodeA == null && barcodeB == null) return;

    setState(() => _isLoadingInitial = true);
    final repo = ref.read(productRepositoryProvider);

    if (barcodeA != null && barcodeA.isNotEmpty) {
      try {
        final prodA = await repo.getProductByBarcode(barcodeA);
        ref.read(comparisonProductAProvider.notifier).state = prodA;
      } catch (_) {}
    }

    if (barcodeB != null && barcodeB.isNotEmpty) {
      try {
        final prodB = await repo.getProductByBarcode(barcodeB);
        ref.read(comparisonProductBProvider.notifier).state = prodB;
      } catch (_) {}
    }

    if (mounted) {
      setState(() => _isLoadingInitial = false);
    }
  }

  void _openProductPicker({required bool isSlotA}) {
    ProductPickerModal.show(
      context,
      slotTitle: isSlotA ? 'Select Product A' : 'Select Product B',
      onProductSelected: (ProductDetailsResponse selected) {
        if (isSlotA) {
          ref.read(comparisonProductAProvider.notifier).state = selected;
        } else {
          ref.read(comparisonProductBProvider.notifier).state = selected;
        }
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final productA = ref.watch(comparisonProductAProvider);
    final productB = ref.watch(comparisonProductBProvider);
    final basis = ref.watch(comparisonBasisProvider);
    final nutrientRows = ref.watch(comparisonNutrientRowsProvider);
    final takeaways = ref.watch(comparisonTakeawaysProvider);
    final choiceSummary = ref.watch(comparisonChoiceSummaryProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F4), // Base warm ivory
      body: Stack(
        children: [
          // Background Lavender Curve
          const Positioned.fill(
            child: CustomPaint(
              painter: _ComparisonLavenderWavePainter(),
            ),
          ),

          // Scrollable Content
          SafeArea(
            child: _isLoadingInitial
                ? const Center(
                    child: CircularProgressIndicator(color: Color(0xFFFF6B35)),
                  )
                : SingleChildScrollView(
                    physics: const BouncingScrollPhysics(),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 12.0),

                        // Section B: Top App Bar & Header
                        const ComparisonTopBar(),

                        const SizedBox(height: 18.0),

                        // Section C: Dual Product Selector Cards + Center VS Badge
                        ComparisonProductCards(
                          productA: productA,
                          productB: productB,
                          basis: basis,
                          onSelectProductA: () => _openProductPicker(isSlotA: true),
                          onSelectProductB: () => _openProductPicker(isSlotA: false),
                          onRemoveProductA: () {
                            ref.read(comparisonProductAProvider.notifier).state = null;
                          },
                          onRemoveProductB: () {
                            ref.read(comparisonProductBProvider.notifier).state = null;
                          },
                          onBasisTap: () {
                            // Toggle between 100 g and Per Serving if available
                            final current = ref.read(comparisonBasisProvider);
                            ref.read(comparisonBasisProvider.notifier).state =
                                current == '100 g' ? 'per serving' : '100 g';
                          },
                        ),

                        const SizedBox(height: 24.0),

                        // Section D: Nutrition Comparison (per 100 g)
                        ComparisonNutritionTable(
                          rows: nutrientRows,
                          basis: basis == '100 g' ? 'per 100 g' : 'per serving',
                        ),

                        const SizedBox(height: 24.0),

                        // Section E: Key Takeaways
                        ComparisonKeyTakeaways(
                          takeaways: takeaways,
                        ),

                        const SizedBox(height: 20.0),

                        // Section F: Ingredients at Glance & Allergen Information
                        ComparisonIngredientsAllergens(
                          productA: productA,
                          productB: productB,
                        ),

                        const SizedBox(height: 16.0),

                        // Section G: Bottom "Your Choice" Sparkle Banner
                        ComparisonYourChoiceBanner(
                          summary: choiceSummary,
                        ),

                        const SizedBox(height: 16.0),
                      ],
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}

/// Custom painter rendering the top-right lavender wave matching Product Comparison.png
class _ComparisonLavenderWavePainter extends CustomPainter {
  const _ComparisonLavenderWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);

    final path = Path();
    path.moveTo(size.width * 0.54, 0);
    path.cubicTo(
      size.width * 0.60,
      size.height * 0.12,
      size.width * 0.40,
      size.height * 0.22,
      size.width * 0.48,
      size.height * 0.38,
    );
    path.cubicTo(
      size.width * 0.56,
      size.height * 0.52,
      size.width * 0.95,
      size.height * 0.56,
      size.width,
      size.height * 0.60,
    );
    path.lineTo(size.width, 0);
    path.close();

    final paint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topRight,
        end: Alignment.bottomLeft,
        colors: [
          Color(0xFFD5C6EC),
          Color(0xFFEFE9F8),
          Color(0x00FDF8F4),
        ],
        stops: [0.0, 0.45, 1.0],
      ).createShader(rect);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
