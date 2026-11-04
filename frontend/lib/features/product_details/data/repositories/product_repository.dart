import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
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
    try {
      final response = await _apiClient.get(
        '${ApiConstants.productEndpoint}/$barcode',
        queryParameters: {
          'include_ai_explanation': includeAiExplanation,
        },
      );

      // Cache product details on device for offline lookup & instant recall
      try {
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('yumsure_product_cache_$barcode', jsonEncode(response));

        // Prepend to local recent scans
        final identity = response['product'] ?? response['product_identity'];
        if (identity is Map<String, dynamic>) {
          const recentKey = 'yumsure_recent_scans_cache';
          final cachedRecent = prefs.getString(recentKey);
          List<dynamic> list = [];
          if (cachedRecent != null) {
            try {
              list = jsonDecode(cachedRecent);
            } catch (_) {}
          }
          list.removeWhere((item) => item is Map && item['barcode'] == barcode);

          final keyFindings = response['key_findings'];
          String? firstFinding;
          String? firstSeverity;
          if (keyFindings is List && keyFindings.isNotEmpty && keyFindings[0] is Map) {
            firstFinding = keyFindings[0]['title']?.toString();
            firstSeverity = keyFindings[0]['severity']?.toString();
          }

          list.insert(0, {
            'barcode': barcode,
            'product_name': identity['product_name'] ?? 'Packaged Product',
            'brand_name': identity['brand_name'],
            'food_category': identity['food_category'] ?? 'Packaged Food',
            'image_url': identity['image_url'],
            'scanned_at': DateTime.now().toIso8601String(),
            'key_finding': firstFinding,
            'key_finding_severity': firstSeverity ?? 'MODERATE',
          });

          if (list.length > 20) {
            list = list.sublist(0, 20);
          }
          await prefs.setString(recentKey, jsonEncode(list));
        }
      } catch (_) {}

      return ProductDetailsResponse.fromJson(response);
    } catch (e) {
      // Offline fallback: check local SharedPreferences cache
      try {
        final prefs = await SharedPreferences.getInstance();
        final cached = prefs.getString('yumsure_product_cache_$barcode');
        if (cached != null && cached.isNotEmpty) {
          return ProductDetailsResponse.fromJson(jsonDecode(cached));
        }
      } catch (_) {}
      rethrow;
    }
  }
}

