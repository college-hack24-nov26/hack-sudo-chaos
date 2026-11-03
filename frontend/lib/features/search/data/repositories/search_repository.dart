import 'package:flutter/material.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/network/api_exceptions.dart';
import '../models/search_models.dart';

abstract class SearchRepository {
  Future<List<SearchResultItem>> searchProducts({
    required String query,
    String? category,
  });

  Future<List<TrendingProductItem>> getTrendingProducts();

  List<PopularSearchItem> getPopularSearches();

  List<CategoryFilterItem> getCategories();
}

class SearchRepositoryImpl implements SearchRepository {
  final ApiClient _apiClient;

  SearchRepositoryImpl({required ApiClient apiClient}) : _apiClient = apiClient;

  @override
  Future<List<SearchResultItem>> searchProducts({
    required String query,
    String? category,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'q': query,
      };
      if (category != null && category.isNotEmpty && category.toLowerCase() != 'all') {
        queryParams['category'] = category;
      }

      final response = await _apiClient.get(
        ApiConstants.searchEndpoint,
        queryParameters: queryParams,
      );

      // 1. Explicitly verify that the response contains an 'items' field
      if (!response.containsKey('items')) {
        throw InvalidResponseException(
          message: 'Search response is missing the required "items" field.',
          expectedField: 'items',
          rawData: response,
        );
      }

      // 2. Verify that 'items' is not null
      final rawItems = response['items'];
      if (rawItems == null) {
        throw InvalidResponseException(
          message: 'Search response field "items" must not be null.',
          expectedField: 'items',
          rawData: response,
        );
      }

      // 3. Verify that 'items' is a List
      if (rawItems is! List) {
        throw InvalidResponseException(
          message: 'Search response field "items" must be a List, but got ${rawItems.runtimeType}.',
          expectedField: 'items',
          rawData: response,
        );
      }

      // 4. Return typed results or empty state when backend returns items: []
      return rawItems
          .whereType<Map<String, dynamic>>()
          .map((item) => SearchResultItem.fromJson(item))
          .toList();
    } on NotFoundException {
      rethrow;
    } on ServerException {
      rethrow;
    } on NetworkException {
      rethrow;
    } on InvalidResponseException {
      rethrow;
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: 'Unexpected error searching products: $e');
    }
  }

  @override
  Future<List<TrendingProductItem>> getTrendingProducts() async {
    try {
      final response = await _apiClient.get(ApiConstants.trendingEndpoint);

      if (!response.containsKey('items')) {
        throw InvalidResponseException(
          message: 'Trending products response is missing "items" field.',
          expectedField: 'items',
          rawData: response,
        );
      }

      final rawItems = response['items'];
      if (rawItems == null || rawItems is! List) {
        throw InvalidResponseException(
          message: 'Trending products response field "items" must be a non-null List.',
          expectedField: 'items',
          rawData: response,
        );
      }

      return rawItems
          .whereType<Map<String, dynamic>>()
          .map((item) => TrendingProductItem.fromJson(item))
          .toList();
    } on NotFoundException {
      rethrow;
    } on ServerException {
      rethrow;
    } on NetworkException {
      rethrow;
    } on InvalidResponseException {
      rethrow;
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: 'Unexpected error fetching trending products: $e');
    }
  }

  @override
  List<PopularSearchItem> getPopularSearches() {
    return const [
      PopularSearchItem(query: 'Chips', isHot: true),
      PopularSearchItem(query: 'Cookies'),
      PopularSearchItem(query: 'Green Tea'),
      PopularSearchItem(query: 'Oats'),
      PopularSearchItem(query: 'Dark Chocolate'),
    ];
  }

  @override
  List<CategoryFilterItem> getCategories() {
    return const [
      CategoryFilterItem(
        id: 'all',
        label: 'All',
        icon: Icons.grid_view_rounded,
      ),
      CategoryFilterItem(
        id: 'snacks',
        label: 'Snacks',
        icon: Icons.bakery_dining_outlined,
      ),
      CategoryFilterItem(
        id: 'beverages',
        label: 'Beverages',
        icon: Icons.local_drink_outlined,
      ),
      CategoryFilterItem(
        id: 'biscuits',
        label: 'Biscuits',
        icon: Icons.cookie_outlined,
      ),
      CategoryFilterItem(
        id: 'dairy',
        label: 'Dairy',
        icon: Icons.water_drop_outlined,
      ),
    ];
  }
}

