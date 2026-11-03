import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../shared/widgets/yumsure_app_bar.dart';
import '../providers/product_details_provider.dart';
import '../widgets/ai_explanation_card.dart';
import '../widgets/allergen_card.dart';
import '../widgets/compare_banner_card.dart';
import '../widgets/fssai_claims_card.dart';
import '../widgets/ingredient_intelligence_card.dart';
import '../widgets/key_findings_card.dart';
import '../widgets/measurement_selector.dart';
import '../widgets/nutrient_row_card.dart';
import '../widgets/nutrition_overview_card.dart';
import '../widgets/product_error_view.dart';
import '../widgets/product_identity_card.dart';
import '../widgets/product_loading_view.dart';

class ProductDetailsScreen extends ConsumerWidget {
  final String barcode;

  const ProductDetailsScreen({
    super.key,
    required this.barcode,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final productAsync = ref.watch(productDetailsFamily(barcode));
    final isPerServing = ref.watch(isPerServingBasisProvider);
    final expandedNutrient = ref.watch(expandedNutrientCodeProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: YumSureAppBar(
        onBack: () {
          if (Navigator.canPop(context)) {
            Navigator.pop(context);
          }
        },
        onBookmark: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Product bookmarking will be enabled in Saved feature phase.'),
              duration: Duration(seconds: 1),
            ),
          );
        },
        onMore: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Product sharing will be available in future phase.'),
              duration: Duration(seconds: 1),
            ),
          );
        },
      ),
      body: productAsync.when(
        loading: () => const ProductLoadingView(),
        error: (err, stack) => ProductErrorView(
          error: err,
          onRetry: () => ref.refresh(productDetailsFamily(barcode)),
        ),
        data: (details) {
          final product = details.product;
          final nutrients = details.nutritionalInterpretation?.nutrients ?? [];

          return RefreshIndicator(
            color: AppColors.brandOrange,
            backgroundColor: Colors.white,
            onRefresh: () async {
              ref.invalidate(productDetailsFamily(barcode));
            },
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
              children: [
                // Section 1: Product Identity Card
                ProductIdentityCard(
                  product: product,
                  isFssaiCompliant: details.regulatoryClaimsValidation?.isFssaiCompliant,
                ),
                const SizedBox(height: AppSpacing.md),

                // Section 2: Measurement Selector (Per 100g vs Per Serving)
                MeasurementSelector(
                  product: product,
                  isPerServing: isPerServing,
                  onSelectionChanged: (val) {
                    ref.read(isPerServingBasisProvider.notifier).state = val;
                  },
                ),
                const SizedBox(height: AppSpacing.lg),

                // Section 3: Nutrition Overview
                NutritionOverviewCard(
                  nutrients: nutrients,
                  isPerServing: isPerServing,
                  foodForm: product.foodForm,
                ),
                const SizedBox(height: AppSpacing.xl),

                // Section 4: Individual Nutrient Details Header & List
                const Text('Nutrient Details', style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
                const SizedBox(height: AppSpacing.md),

                if (nutrients.isEmpty) ...[
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 16.0),
                    child: Center(
                      child: Text(
                        'No nutrient data declared on packaging.',
                        style: TextStyle(fontStyle: FontStyle.italic, color: AppColors.textSecondary),
                      ),
                    ),
                  ),
                ] else ...[
                  ...nutrients.map((n) {
                    return NutrientRowCard(
                      nutrient: n,
                      isPerServing: isPerServing,
                      isExpanded: expandedNutrient == n.nutrientCode,
                      onToggleExpand: () {
                        final current = ref.read(expandedNutrientCodeProvider);
                        ref.read(expandedNutrientCodeProvider.notifier).state =
                            current == n.nutrientCode ? null : n.nutrientCode;
                      },
                    );
                  }),
                ],
                const SizedBox(height: AppSpacing.lg),

                // Section 5 & 6: Key Findings & Ingredient Intelligence (Two-card layout)
                LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth > 500) {
                      return Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(child: KeyFindingsCard(findings: details.keyFindings)),
                          const SizedBox(width: AppSpacing.md),
                          Expanded(
                            child: IngredientIntelligenceCard(
                              ingredientAnalysis: details.ingredientAnalysis,
                              onNavigateToDetails: () {
                                context.push('/product/${details.product.barcode}/ingredients');
                              },
                            ),
                          ),
                        ],
                      );
                    } else {
                      return Column(
                        children: [
                          KeyFindingsCard(findings: details.keyFindings),
                          const SizedBox(height: AppSpacing.md),
                          IngredientIntelligenceCard(
                              ingredientAnalysis: details.ingredientAnalysis,
                              onNavigateToDetails: () {
                                context.push('/product/${details.product.barcode}/ingredients');
                              },
                            ),
                        ],
                      );
                    }
                  },
                ),
                const SizedBox(height: AppSpacing.md),

                // Section 7 & 8: Allergen Information & FSSAI Claim Verification
                LayoutBuilder(
                  builder: (context, constraints) {
                    if (constraints.maxWidth > 500) {
                      return Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: AllergenCard(
                              ingredientAnalysis: details.ingredientAnalysis,
                            ),
                          ),
                          const SizedBox(width: AppSpacing.md),
                          Expanded(
                            child: FssaiClaimsCard(
                              claimsValidation: details.regulatoryClaimsValidation,
                              onNavigateToDetails: () {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('FSSAI Claim Details screen integration point prepared.'),
                                  ),
                                );
                              },
                            ),
                          ),
                        ],
                      );
                    } else {
                      return Column(
                        children: [
                          AllergenCard(
                            ingredientAnalysis: details.ingredientAnalysis,
                          ),
                          const SizedBox(height: AppSpacing.md),
                          FssaiClaimsCard(
                            claimsValidation: details.regulatoryClaimsValidation,
                            onNavigateToDetails: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(
                                  content: Text('FSSAI Claim Details screen integration point prepared.'),
                                ),
                              );
                            },
                          ),
                        ],
                      );
                    }
                  },
                ),
                const SizedBox(height: AppSpacing.md),

                // Section 9: AI Explanation (Rendered only if available)
                if (details.aiExplanation != null) ...[
                  AiExplanationCard(
                    aiExplanation: details.aiExplanation,
                    onNavigateToFullExplanation: () {
                      context.push('/product/${details.product.barcode}/ai-explanation');
                    },
                  ),
                  const SizedBox(height: AppSpacing.md),
                ],

                // Section 10: Product Comparison Action Banner
                CompareBannerCard(
                  onCompare: () {
                    context.push('/compare?productA=${details.product.barcode}');
                  },
                ),
                const SizedBox(height: AppSpacing.xxxl),
              ],
            ),
          );
        },
      ),
    );
  }
}

