import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/api_client.dart';
import '../../data/models/product_response_model.dart';
import '../../data/repositories/product_repository.dart';

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

final productRepositoryProvider = Provider<ProductRepository>((ref) {
  final client = ref.watch(apiClientProvider);
  return ProductRepositoryImpl(apiClient: client);
});

/// Controls whether the screen is viewing 'Per 100 g' (false) or 'Per Serving' (true)
final isPerServingBasisProvider = StateProvider.autoDispose<bool>((ref) => false);

/// Controls expanded/collapsed state for nutrient cards
final expandedNutrientCodeProvider = StateProvider.autoDispose<String?>((ref) => null);

/// Fetches the product details for a given barcode
final productDetailsFamily = FutureProvider.autoDispose.family<ProductDetailsResponse, String>((ref, barcode) async {
  final repo = ref.watch(productRepositoryProvider);
  return await repo.getProductByBarcode(barcode);
});

