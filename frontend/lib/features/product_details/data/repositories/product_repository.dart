import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/api_client.dart';
import '../models/product_response_model.dart';

abstract class ProductRepository {
  Future<ProductDetailsResponse> getProductByBarcode(
    String barcode, {
    bool includeAiExplanation = true,
  });
}

class ProductRepositoryImpl implements ProductRepository {
  final ApiClient _apiClient;

  ProductRepositoryImpl({required ApiClient apiClient}) : _apiClient = apiClient;

  @override
  Future<ProductDetailsResponse> getProductByBarcode(
    String barcode, {
    bool includeAiExplanation = true,
  }) async {
    final response = await _apiClient.get(
      '${ApiConstants.productEndpoint}/$barcode',
      queryParameters: {
        'include_ai_explanation': includeAiExplanation,
      },
    );

    return ProductDetailsResponse.fromJson(response);
  }
}

