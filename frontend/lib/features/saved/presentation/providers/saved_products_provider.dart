import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/saved_product_model.dart';
import '../../data/repositories/saved_products_repository.dart';

final savedProductsRepositoryProvider = Provider<SavedProductsRepository>((ref) {
  return SavedProductsRepositoryImpl();
});

class SavedProductsNotifier extends StateNotifier<AsyncValue<List<SavedProductItem>>> {
  final SavedProductsRepository _repository;

  SavedProductsNotifier({required SavedProductsRepository repository})
      : _repository = repository,
        super(const AsyncValue.loading()) {
    loadSavedProducts();
  }

  Future<void> loadSavedProducts() async {
    state = const AsyncValue.loading();
    try {
      final items = await _repository.getSavedProducts();
      state = AsyncValue.data(items);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }

  Future<void> removeProduct(String barcode) async {
    final currentList = state.valueOrNull ?? [];
    final updated = currentList.where((p) => p.barcode != barcode).toList();
    state = AsyncValue.data(updated);
    await _repository.removeProduct(barcode);
  }

  Future<void> saveProduct(SavedProductItem product) async {
    final currentList = state.valueOrNull ?? [];
    final filtered = currentList.where((p) => p.barcode != product.barcode).toList();
    filtered.insert(0, product);
    state = AsyncValue.data(filtered);
    await _repository.saveProduct(product);
  }
}

final savedProductsNotifierProvider =
    StateNotifierProvider<SavedProductsNotifier, AsyncValue<List<SavedProductItem>>>((ref) {
  final repo = ref.watch(savedProductsRepositoryProvider);
  return SavedProductsNotifier(repository: repo);
});

final selectedSavedCategoryProvider = StateProvider<String>((ref) => 'all');

final savedSearchQueryProvider = StateProvider<String>((ref) => '');

final isSavedSearchExpandedProvider = StateProvider<bool>((ref) => false);

final savedSortOrderProvider = StateProvider<SavedSortOrder>((ref) => SavedSortOrder.recentlySaved);

/// Category counts map: {'all': N, 'snacks': N, 'beverages': N, 'biscuits': N, 'dairy': N}
final savedCategoryCountsProvider = Provider<Map<String, int>>((ref) {
  final asyncList = ref.watch(savedProductsNotifierProvider);
  final items = asyncList.valueOrNull ?? [];

  int all = items.length;
  int snacks = 0;
  int beverages = 0;
  int biscuits = 0;
  int dairy = 0;

  for (final item in items) {
    final cat = item.category.trim().toLowerCase();
    if (cat.contains('snack') || cat.contains('chip') || cat.contains('namkeen')) {
      snacks++;
    } else if (cat.contains('beverage') || cat.contains('drink') || cat.contains('cola') || cat.contains('tea') || cat.contains('juice')) {
      beverages++;
    } else if (cat.contains('biscuit') || cat.contains('cookie')) {
      biscuits++;
    } else if (cat.contains('dairy') || cat.contains('milk') || cat.contains('cheese') || cat.contains('curd')) {
      dairy++;
    }
  }

  return {
    'all': all,
    'snacks': snacks,
    'beverages': beverages,
    'biscuits': biscuits,
    'dairy': dairy,
  };
});

/// Filtered & Sorted list derived from selected category, search query, and sort order
final filteredSavedProductsProvider = Provider<AsyncValue<List<SavedProductItem>>>((ref) {
  final asyncItems = ref.watch(savedProductsNotifierProvider);
  final category = ref.watch(selectedSavedCategoryProvider).toLowerCase();
  final query = ref.watch(savedSearchQueryProvider).trim().toLowerCase();
  final sortOrder = ref.watch(savedSortOrderProvider);

  return asyncItems.whenData((items) {
    var result = List<SavedProductItem>.from(items);

    // 1. Filter by category
    if (category != 'all' && category.isNotEmpty) {
      result = result.where((item) {
        final c = item.category.toLowerCase();
        if (category == 'snacks') {
          return c.contains('snack') || c.contains('chip') || c.contains('namkeen');
        } else if (category == 'beverages') {
          return c.contains('beverage') || c.contains('drink') || c.contains('cola') || c.contains('tea') || c.contains('juice');
        } else if (category == 'biscuits') {
          return c.contains('biscuit') || c.contains('cookie');
        } else if (category == 'dairy') {
          return c.contains('dairy') || c.contains('milk') || c.contains('cheese');
        }
        return c.contains(category);
      }).toList();
    }

    // 2. Filter by search query
    if (query.isNotEmpty) {
      result = result.where((item) {
        final nameMatch = item.productName.toLowerCase().contains(query);
        final brandMatch = item.brandOrQuantity.toLowerCase().contains(query);
        final catMatch = item.category.toLowerCase().contains(query);
        return nameMatch || brandMatch || catMatch;
      }).toList();
    }

    // 3. Sort order
    if (sortOrder == SavedSortOrder.alphabetical) {
      result.sort((a, b) => a.productName.toLowerCase().compareTo(b.productName.toLowerCase()));
    } else {
      result.sort((a, b) => b.savedAt.compareTo(a.savedAt));
    }

    return result;
  });
});

