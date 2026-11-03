import 'package:flutter/material.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/network/api_exceptions.dart';
import '../models/home_models.dart';

abstract class HomeRepository {
  Future<List<ScanHistoryItem>> getRecentScans({int limit = 5});
  Future<ScanInsight?> getScanInsights({String timeframe = '7d'});
  List<CategoryItem> getCategories();
}

class HomeRepositoryImpl implements HomeRepository {
  final ApiClient _apiClient;

  HomeRepositoryImpl({required ApiClient apiClient}) : _apiClient = apiClient;

  @override
  Future<List<ScanHistoryItem>> getRecentScans({int limit = 5}) async {
    try {
      final response = await _apiClient.get(
        ApiConstants.historyEndpoint,
        queryParameters: {'limit': limit},
      );

      // 1. Explicitly verify that the response contains an 'items' field
      if (!response.containsKey('items')) {
        throw InvalidResponseException(
          message: 'Scan history response is missing the required "items" field.',
          expectedField: 'items',
          rawData: response,
        );
      }

      // 2. Verify that 'items' is not null
      final rawItems = response['items'];
      if (rawItems == null) {
        throw InvalidResponseException(
          message: 'Scan history response field "items" must not be null.',
          expectedField: 'items',
          rawData: response,
        );
      }

      // 3. Verify that 'items' is a List
      if (rawItems is! List) {
        throw InvalidResponseException(
          message: 'Scan history response field "items" must be a List, but got ${rawItems.runtimeType}.',
          expectedField: 'items',
          rawData: response,
        );
      }

      // 4. Only return an empty list when the backend explicitly returns {"items": []}
      if (rawItems.isEmpty) {
        return const [];
      }

      // 5. Verify and map each item in the list
      return rawItems.map((e) {
        if (e is! Map<String, dynamic>) {
          throw InvalidResponseException(
            message: 'Each entry in "items" must be a JSON object, but got ${e.runtimeType}.',
            expectedField: 'items',
            rawData: e,
          );
        }
        return ScanHistoryItem.fromJson(e);
      }).toList();
    } on NotFoundException {
      // HTTP 404: Resource or endpoint not found on server
      rethrow;
    } on ServerException {
      // HTTP 500 / 5xx: Backend internal server error
      rethrow;
    } on NetworkException {
      // Network failure / Connection unreachable
      rethrow;
    } on InvalidResponseException {
      // Malformed JSON / missing structure
      rethrow;
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: 'Unexpected error fetching scan history: $e');
    }
  }

  @override
  Future<ScanInsight?> getScanInsights({String timeframe = '7d'}) async {
    try {
      final response = await _apiClient.get(
        ApiConstants.historyInsightsEndpoint,
        queryParameters: {'timeframe': timeframe},
      );

      // 1. Explicitly verify that the response contains an 'insight' field
      if (!response.containsKey('insight')) {
        throw InvalidResponseException(
          message: 'Scan insights response is missing the required "insight" field.',
          expectedField: 'insight',
          rawData: response,
        );
      }

      final rawInsight = response['insight'];

      // 2. Legitimate empty state: backend explicitly returns {"insight": null}
      if (rawInsight == null) {
        return null;
      }

      // 3. If present, verify that 'insight' is a Map<String, dynamic>
      if (rawInsight is! Map<String, dynamic>) {
        throw InvalidResponseException(
          message: 'Scan insights response field "insight" must be a JSON object or null, but got ${rawInsight.runtimeType}.',
          expectedField: 'insight',
          rawData: response,
        );
      }

      return ScanInsight.fromJson(rawInsight);
    } on NotFoundException {
      // HTTP 404: Resource or endpoint not found on server
      rethrow;
    } on ServerException {
      // HTTP 500 / 5xx: Backend internal server error
      rethrow;
    } on NetworkException {
      // Network failure / Connection unreachable
      rethrow;
    } on InvalidResponseException {
      // Malformed JSON / missing structure
      rethrow;
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: 'Unexpected error fetching scan insights: $e');
    }
  }

  @override
  List<CategoryItem> getCategories() {
    return const [
      CategoryItem(
        id: 'snacks',
        title: 'Snacks',
        icon: Icons.bakery_dining_rounded,
        gradientColors: [Color(0xFFE5A663), Color(0xFFC97C36)],
        assetImagePath: 'assets/images/cat_snacks.webp',
      ),
      CategoryItem(
        id: 'beverages',
        title: 'Beverages',
        icon: Icons.local_drink_rounded,
        gradientColors: [Color(0xFF3E2723), Color(0xFF1B0000)],
        assetImagePath: 'assets/images/cat_beverages.webp',
      ),
      CategoryItem(
        id: 'biscuits',
        title: 'Biscuits',
        icon: Icons.cookie_rounded,
        gradientColors: [Color(0xFFD49A6A), Color(0xFFA66D3B)],
        assetImagePath: 'assets/images/cat_biscuits.webp',
      ),
      CategoryItem(
        id: 'dairy',
        title: 'Dairy',
        icon: Icons.water_drop_rounded,
        gradientColors: [Color(0xFFB0BEC5), Color(0xFF78909C)],
        assetImagePath: 'assets/images/cat_dairy.webp',
      ),
    ];
  }
}
