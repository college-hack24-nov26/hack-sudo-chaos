import 'package:go_router/go_router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../../data/models/ingredient_intelligence_model.dart';
import '../widgets/ingredient_additives_section.dart';
import '../widgets/ingredient_disclaimer_card.dart';
import '../widgets/ingredient_filter_pills.dart';
import '../widgets/ingredient_intelligence_card_item.dart';
import '../widgets/ingredient_overall_insight_card.dart';
import '../widgets/ingredient_product_summary_card.dart';
import '../widgets/ingredient_raw_list_card.dart';
import '../widgets/ingredient_top_app_bar.dart';

class IngredientDetailsScreen extends ConsumerStatefulWidget {
  final String barcode;

  const IngredientDetailsScreen({
    super.key,
    required this.barcode,
  });

  @override
  ConsumerState<IngredientDetailsScreen> createState() => _IngredientDetailsScreenState();
}

class _IngredientDetailsScreenState extends ConsumerState<IngredientDetailsScreen> {
  String _activeSection = 'ingredients';

  final ScrollController _scrollController = ScrollController();
  final GlobalControllerKeys _keys = GlobalControllerKeys();

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToSection(String sectionKey) {
    setState(() => _activeSection = sectionKey);

    BuildContext? targetContext;
    if (sectionKey == 'ingredients') {
      targetContext = _keys.ingredientsKey.currentContext;
    } else if (sectionKey == 'additives') {
      targetContext = _keys.additivesKey.currentContext;
    } else if (sectionKey == 'allergens') {
      context.push('/product/${widget.barcode}/allergens');
      return;
    } else if (sectionKey == 'claims') {
      targetContext = _keys.claimsKey.currentContext;
    }

    if (targetContext != null) {
      Scrollable.ensureVisible(
        targetContext,
        duration: const Duration(milliseconds: 350),
        curve: Curves.easeInOut,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final productAsync = ref.watch(productDetailsFamily(widget.barcode));

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F4), // Base warm ivory
      body: Stack(
        children: [
          // Background Lavender Curve
          const Positioned.fill(
            child: CustomPaint(
              painter: _IngredientLavenderWavePainter(),
            ),
          ),

          // Scrollable Content
          SafeArea(
            child: productAsync.when(
              loading: () => const Column(
                children: [
                  IngredientTopAppBar(product: null),
                  Expanded(
                    child: Center(
                      child: CircularProgressIndicator(color: Color(0xFFFF6B35)),
                    ),
                  ),
                ],
              ),
              error: (err, _) => Column(
                children: [
                  const IngredientTopAppBar(product: null),
                  Expanded(
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(
                              Icons.wifi_off_rounded,
                              size: 48.0,
                              color: Color(0xFF8E8A93),
                            ),
                            const SizedBox(height: 14.0),
                            const Text(
                              'Unable to load ingredient data',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 16.0,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF141414),
                              ),
                            ),
                            const SizedBox(height: 6.0),
                            Text(
                              err.toString(),
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 12.0,
                                color: Color(0xFF6E6877),
                              ),
                            ),
                            const SizedBox(height: 18.0),
                            ElevatedButton(
                              onPressed: () => ref.refresh(productDetailsFamily(widget.barcode)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFFFF6B35),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(16.0),
                                ),
                              ),
                              child: const Text(
                                'Retry',
                                style: TextStyle(
                                  fontFamily: 'Manrope',
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              data: (details) {
                final ingredients = IngredientIntelligenceHelper.extractIngredients(details);
                final insight = IngredientIntelligenceHelper.generateOverallInsight(details, ingredients);
                final rawText = details.ingredientAnalysis?.ingredientsSummary;

                return SingleChildScrollView(
                  controller: _scrollController,
                  physics: const BouncingScrollPhysics(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Section B: Top App Bar
                      IngredientTopAppBar(product: details),

                      const SizedBox(height: 8.0),

                      // Section C: Top Product Summary Card
                      IngredientProductSummaryCard(product: details),

                      const SizedBox(height: 16.0),

                      // Section D: 4 Horizontal Section / Filter Pills
                      IngredientFilterPills(
                        activeSection: _activeSection,
                        onSelectSection: _scrollToSection,
                      ),

                      const SizedBox(height: 20.0),

                      // Section E: Ingredient List (Raw)
                      KeyedSubtree(
                        key: _keys.ingredientsKey,
                        child: IngredientRawListCard(rawText: rawText),
                      ),

                      const SizedBox(height: 24.0),

                      // Section F: Ingredient Intelligence Section
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Ingredient Intelligence',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 18.0,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.3,
                                color: Color(0xFF141414),
                              ),
                            ),
                            const SizedBox(height: 3.0),
                            const Text(
                              'What each ingredient does and how it affects your nutrition.',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 12.8,
                                fontWeight: FontWeight.w400,
                                color: Color(0xFF4A4552),
                              ),
                            ),
                            const SizedBox(height: 14.0),

                            if (ingredients.isEmpty)
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(16.0),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFAF7F5),
                                  borderRadius: BorderRadius.circular(18.0),
                                  border: Border.all(color: Colors.white, width: 1.5),
                                ),
                                child: const Center(
                                  child: Text(
                                    'Detailed ingredient breakdown not declared for this product.',
                                    style: TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 13.0,
                                      color: Color(0xFF6E6877),
                                    ),
                                  ),
                                ),
                              )
                            else
                              ListView.builder(
                                shrinkWrap: true,
                                physics: const NeverScrollableScrollPhysics(),
                                itemCount: ingredients.length,
                                itemBuilder: (context, index) {
                                  return IngredientIntelligenceCardItem(
                                    item: ingredients[index],
                                  );
                                },
                              ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 10.0),

                      // Section G: Overall Insight Split Card
                      IngredientOverallInsightCard(insightText: insight),

                      // Section H: Additives & Processing Section
                      KeyedSubtree(
                        key: _keys.additivesKey,
                        child: IngredientAdditivesSection(items: ingredients),
                      ),

                      // Allergens anchor
                      KeyedSubtree(
                        key: _keys.allergensKey,
                        child: const SizedBox(height: 1.0),
                      ),

                      // Claims anchor
                      KeyedSubtree(
                        key: _keys.claimsKey,
                        child: const SizedBox(height: 1.0),
                      ),

                      // Bottom Regulatory & Label Disclaimer Card
                      const IngredientDisclaimerCard(),
                    ],
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class GlobalControllerKeys {
  final GlobalKey ingredientsKey = GlobalKey();
  final GlobalKey additivesKey = GlobalKey();
  final GlobalKey allergensKey = GlobalKey();
  final GlobalKey claimsKey = GlobalKey();
}

/// Custom painter for the top-right lavender wave in Ingredient Details
class _IngredientLavenderWavePainter extends CustomPainter {
  const _IngredientLavenderWavePainter();

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
