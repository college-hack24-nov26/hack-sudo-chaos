class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final String? errorType;
  final dynamic rawData;

  const ApiException({
    required this.message,
    this.statusCode,
    this.errorType,
    this.rawData,
  });

  @override
  String toString() => 'ApiException: $message (Status: $statusCode, Type: $errorType)';
}

/// HTTP 404: Endpoint, route, or resource not found on backend
class NotFoundException extends ApiException {
  final String? resourcePath;

  const NotFoundException({
    required super.message,
    this.resourcePath,
    super.statusCode = 404,
    super.errorType = 'RESOURCE_NOT_FOUND',
    super.rawData,
  });
}

/// HTTP 404 specific to a packaged food product barcode lookup
class ProductNotFoundException extends NotFoundException {
  final String barcode;

  const ProductNotFoundException({
    required this.barcode,
    String? message,
    super.rawData,
  }) : super(
          message: message ?? 'Product with barcode $barcode was not found in database or Open Food Facts.',
          resourcePath: barcode,
          errorType: 'PRODUCT_NOT_FOUND',
        );
}

/// HTTP 500 / 5xx: Backend server error or gateway failure
class ServerException extends ApiException {
  const ServerException({
    required super.message,
    required super.statusCode,
    super.errorType = 'INTERNAL_SERVER_ERROR',
    super.rawData,
  });
}

/// Network failure: connection timeout, connection refused, offline host
class NetworkException extends ApiException {
  const NetworkException({required super.message})
      : super(
          statusCode: null,
          errorType: 'NETWORK_UNREACHABLE',
        );
}

/// Thrown when the backend returns an HTTP response with missing, null, or malformed structure
class InvalidResponseException extends ApiException {
  final String? expectedField;

  const InvalidResponseException({
    required super.message,
    this.expectedField,
    super.statusCode = 200,
    super.errorType = 'INVALID_RESPONSE_STRUCTURE',
    super.rawData,
  });
}
