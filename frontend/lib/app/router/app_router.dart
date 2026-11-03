import 'package:go_router/go_router.dart';
import '../../features/ai_explanation/presentation/screens/ai_explanation_placeholder_screen.dart';
import '../../features/comparison/presentation/screens/product_comparison_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/ingredients/presentation/screens/ingredient_details_screen.dart';
import '../../features/product_details/presentation/screens/product_details_screen.dart';
import '../../features/saved/presentation/screens/saved_products_screen.dart';
import '../../features/scanner/presentation/screens/scanner_screen.dart';
import '../../features/search/presentation/screens/search_screen.dart';

class AppRoutes {
  static const String root = '/';
  static const String home = '/home';
  static const String productDetails = '/product/:barcode';
  static const String search = '/search';
  static const String scanner = '/scanner';
  static const String saved = '/saved';
  static const String comparison = '/comparison';
  static const String compare = '/compare';
  static const String ingredients = '/ingredients';
  static const String aiExplanation = '/ai-explanation';
}

final GoRouter appRouter = GoRouter(
  // Correct initial route: Fresh application launch opens Home
  initialLocation: AppRoutes.home,
  routes: [
    GoRoute(
      path: AppRoutes.root,
      redirect: (context, state) => AppRoutes.home,
    ),
    GoRoute(
      path: AppRoutes.home,
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: AppRoutes.productDetails,
      builder: (context, state) {
        final barcode = state.pathParameters['barcode'] ?? '';
        return ProductDetailsScreen(barcode: barcode);
      },
    ),
    GoRoute(
      path: AppRoutes.search,
      builder: (context, state) => SearchScreen(
        initialCategory: state.uri.queryParameters['category'],
      ),
    ),
    GoRoute(
      path: AppRoutes.scanner,
      builder: (context, state) => const ScannerScreen(),
    ),
    GoRoute(
      path: AppRoutes.saved,
      builder: (context, state) => const SavedProductsScreen(),
    ),
    GoRoute(
      path: AppRoutes.compare,
      redirect: (context, state) {
        final q = state.uri.query;
        return q.isEmpty ? AppRoutes.comparison : '${AppRoutes.comparison}?$q';
      },
    ),
    GoRoute(
      path: AppRoutes.comparison,
      builder: (context, state) => ProductComparisonScreen(
        initialProductABarcode: state.uri.queryParameters['productA'],
        initialProductBBarcode: state.uri.queryParameters['productB'],
      ),
    ),
    GoRoute(
      path: AppRoutes.ingredients,
      builder: (context, state) {
        final barcode = state.uri.queryParameters['barcode'] ?? '';
        return IngredientDetailsScreen(barcode: barcode);
      },
    ),
    GoRoute(
      path: '/product/:barcode/ingredients',
      builder: (context, state) {
        final barcode = state.pathParameters['barcode'] ?? '';
        return IngredientDetailsScreen(barcode: barcode);
      },
    ),
    GoRoute(
      path: AppRoutes.aiExplanation,
      builder: (context, state) => const AiExplanationPlaceholderScreen(),
    ),
  ],
);
