import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../product_details/data/models/product_response_model.dart';
import '../../data/models/comparison_models.dart';

final comparisonProductAProvider = StateProvider<ProductDetailsResponse?>((ref) => null);

final comparisonProductBProvider = StateProvider<ProductDetailsResponse?>((ref) => null);

final comparisonBasisProvider = StateProvider<String>((ref) => '100 g');

final isComparisonLoadingProvider = StateProvider<bool>((ref) => false);

final comparisonNutrientRowsProvider = Provider<List<ComparisonNutrientRow>>((ref) {
  final prodA = ref.watch(comparisonProductAProvider);
  final prodB = ref.watch(comparisonProductBProvider);
  return ComparisonAnalysisHelper.computeNutrientRows(productA: prodA, productB: prodB);
});

final comparisonTakeawaysProvider = Provider<List<ComparisonTakeaway>>((ref) {
  final prodA = ref.watch(comparisonProductAProvider);
  final prodB = ref.watch(comparisonProductBProvider);
  return ComparisonAnalysisHelper.computeTakeaways(productA: prodA, productB: prodB);
});

final comparisonChoiceSummaryProvider = Provider<String>((ref) {
  final prodA = ref.watch(comparisonProductAProvider);
  final prodB = ref.watch(comparisonProductBProvider);
  return ComparisonAnalysisHelper.computeYourChoiceSummary(productA: prodA, productB: prodB);
});
