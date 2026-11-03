import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../../data/models/search_models.dart';
import '../../data/repositories/search_repository.dart';

final searchRepositoryProvider = Provider<SearchRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return SearchRepositoryImpl(apiClient: apiClient);
});

final searchCategoriesProvider = Provider<List<CategoryFilterItem>>((ref) {
  final repo = ref.watch(searchRepositoryProvider);
  return repo.getCategories();
});

final popularSearchesProvider = Provider<List<PopularSearchItem>>((ref) {
  final repo = ref.watch(searchRepositoryProvider);
  return repo.getPopularSearches();
});

final selectedCategoryProvider = StateProvider<String>((ref) => 'all');

final searchQueryProvider = StateProvider<String>((ref) => '');

final trendingProductsProvider = FutureProvider.autoDispose<List<TrendingProductItem>>((ref) async {
  final repo = ref.watch(searchRepositoryProvider);
  return await repo.getTrendingProducts();
});

final searchResultsProvider = FutureProvider.autoDispose<List<SearchResultItem>>((ref) async {
  final query = ref.watch(searchQueryProvider).trim();
  final category = ref.watch(selectedCategoryProvider);
  final repo = ref.watch(searchRepositoryProvider);

  // If both query is empty and category is 'all', we don't query search API
  if (query.isEmpty && (category == 'all' || category.isEmpty)) {
    return const [];
  }

  return await repo.searchProducts(
    query: query,
    category: category != 'all' ? category : null,
  );
});

