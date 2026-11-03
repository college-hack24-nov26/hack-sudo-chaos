import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/saved_product_model.dart';

abstract class SavedProductsRepository {
  Future<List<SavedProductItem>> getSavedProducts();
  Future<void> saveProduct(SavedProductItem product);
  Future<void> removeProduct(String barcode);
  Future<bool> isProductSaved(String barcode);
  Future<void> clearAll();
}

class SavedProductsRepositoryImpl implements SavedProductsRepository {
  static const String _storageKey = 'yumsure_saved_products_v1';

  @override
  Future<List<SavedProductItem>> getSavedProducts() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final jsonString = prefs.getString(_storageKey);
      if (jsonString == null || jsonString.trim().isEmpty) {
        return const [];
      }

      final dynamic decoded = jsonDecode(jsonString);
      if (decoded is List) {
        return decoded
            .whereType<Map<String, dynamic>>()
            .map((item) => SavedProductItem.fromJson(item))
            .toList();
      }
      return const [];
    } catch (_) {
      return const [];
    }
  }

  @override
  Future<void> saveProduct(SavedProductItem product) async {
    final prefs = await SharedPreferences.getInstance();
    final currentList = await getSavedProducts();

    // Remove any existing copy of the same barcode
    final filtered = currentList.where((p) => p.barcode != product.barcode).toList();
    // Insert at front (most recently saved first)
    filtered.insert(0, product);

    final jsonString = jsonEncode(filtered.map((p) => p.toJson()).toList());
    await prefs.setString(_storageKey, jsonString);
  }

  @override
  Future<void> removeProduct(String barcode) async {
    final prefs = await SharedPreferences.getInstance();
    final currentList = await getSavedProducts();

    final filtered = currentList.where((p) => p.barcode != barcode).toList();
    final jsonString = jsonEncode(filtered.map((p) => p.toJson()).toList());
    await prefs.setString(_storageKey, jsonString);
  }

  @override
  Future<bool> isProductSaved(String barcode) async {
    final currentList = await getSavedProducts();
    return currentList.any((p) => p.barcode == barcode);
  }

  @override
  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_storageKey);
  }
}

