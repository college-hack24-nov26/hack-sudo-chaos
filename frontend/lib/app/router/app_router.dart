import 'package:go_router/go_router.dart';
import '../../features/ai_explanation/presentation/screens/ai_food_explanation_screen.dart';
import '../../features/comparison/presentation/screens/product_comparison_screen.dart';
import '../../features/home/presentation/screens/home_screen.dart';
import '../../features/ingredients/presentation/screens/ingredient_details_screen.dart';
import '../../features/product_details/presentation/screens/product_details_screen.dart';
import '../../features/saved/presentation/screens/saved_products_screen.dart';
import '../../features/scanner/presentation/screens/product_loading_screen.dart';
import '../../features/scanner/presentation/screens/product_not_found_screen.dart';
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
  static const String productLoading = '/product-loading/:barcode';
  static const String productNotFound = '/product-not-found/:barcode';
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
      builder: (context, state) {
        final barcode = state.uri.queryParameters['barcode'] ?? '';
        return AiFoodExplanationScreen(barcode: barcode);
      },
    ),
    GoRoute(
      path: '/product/:barcode/ai-explanation',
      builder: (context, state) {
        final barcode = state.pathParameters['barcode'] ?? '';
        return AiFoodExplanationScreen(barcode: barcode);
      },
    ),
    GoRoute(
      path: AppRoutes.productLoading,
      builder: (context, state) {
        final barcode = state.pathParameters['barcode'] ?? '';
        return ProductLoadingScreen(barcode: barcode);
      },
    ),
    GoRoute(
      path: AppRoutes.productNotFound,
      builder: (context, state) {
        final barcode = state.pathParameters['barcode'] ?? '';
        return ProductNotFoundScreen(barcode: barcode);
      },
    ),
  ],
);
