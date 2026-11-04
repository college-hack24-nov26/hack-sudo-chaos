class ApiConstants {
  ApiConstants._();

  static const String apiVersion = '/api/v1';
  static const String productEndpoint = '$apiVersion/products';
  static const String searchEndpoint = '$apiVersion/search';
  static const String trendingEndpoint = '$apiVersion/trending';
  static const String historyEndpoint = '$apiVersion/history';
  static const String historyInsightsEndpoint = '$apiVersion/history/insights';
  static const String chatEndpoint = '$apiVersion/chat/product-qa';
  static const String healthEndpoint = '/health';
}
