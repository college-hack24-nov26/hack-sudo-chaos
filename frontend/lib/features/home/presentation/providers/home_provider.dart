import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../features/product_details/presentation/providers/product_details_provider.dart';
import '../../data/models/home_models.dart';
import '../../data/repositories/home_repository.dart';

final homeRepositoryProvider = Provider<HomeRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  return HomeRepositoryImpl(apiClient: apiClient);
});

final homeCategoriesProvider = Provider<List<CategoryItem>>((ref) {
  final repo = ref.watch(homeRepositoryProvider);
  return repo.getCategories();
});

/// Timeframe state: '7d' (Last 7 days), '30d' (Last 30 days), 'all' (All time)
final selectedInsightTimeframeProvider = StateProvider<String>((ref) => '7d');

/// Recent Scans list provider
final recentScansProvider = FutureProvider.autoDispose<List<ScanHistoryItem>>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  return await repo.getRecentScans(limit: 5);
});

/// Scan Insights provider derived from selected timeframe
final scanInsightsProvider = FutureProvider.autoDispose<ScanInsight?>((ref) async {
  final repo = ref.watch(homeRepositoryProvider);
  final timeframe = ref.watch(selectedInsightTimeframeProvider);
  return await repo.getScanInsights(timeframe: timeframe);
});

