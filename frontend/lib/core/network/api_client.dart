import 'package:dio/dio.dart';
import '../config/env_config.dart';
import 'api_exceptions.dart';

class ApiClient {
  late final Dio _dio;

  ApiClient({String? baseUrl, Dio? dio}) {
    _dio = dio ??
        Dio(
          BaseOptions(
            baseUrl: baseUrl ?? EnvConfig.baseUrl,
            connectTimeout: EnvConfig.connectTimeout,
            receiveTimeout: EnvConfig.receiveTimeout,
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
              'User-Agent': 'YumSure-Flutter/1.0.0 (Android; client)',
            },
          ),
        );
  }

  Future<Map<String, dynamic>> get(
    String path, {
    Map<String, dynamic>? queryParameters,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParameters);
      if (response.data is Map<String, dynamic>) {
        return response.data as Map<String, dynamic>;
      } else {
        throw const ApiException(
          message: 'Unexpected non-JSON response from server',
          errorType: 'INVALID_RESPONSE_FORMAT',
        );
      }
    } on DioException catch (e) {
      throw _handleDioError(e);
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException(message: 'Unexpected error: $e');
    }
  }

  ApiException _handleDioError(DioException error) {
    final response = error.response;
    final statusCode = response?.statusCode;
    final data = response?.data;
    final path = error.requestOptions.path;

    String message = 'Unable to connect to YumSure backend';
    String? errorType;

    if (data is Map<String, dynamic>) {
      message = data['detail']?.toString() ?? data['title']?.toString() ?? message;
      errorType = data['type']?.toString();
    }

    // HTTP 404: Endpoint or Resource Not Found
    if (statusCode == 404) {
      if (path.contains('/products/')) {
        final barcode = path.split('/products/').last.split('?').first;
        return ProductNotFoundException(
          barcode: barcode,
          message: message != 'Unable to connect to YumSure backend' ? message : null,
          rawData: data,
        );
      }
      return NotFoundException(
        message: message != 'Unable to connect to YumSure backend'
            ? message
            : 'Requested endpoint or resource "$path" was not found on the server (HTTP 404).',
        resourcePath: path,
        rawData: data,
      );
    }

    // HTTP 500 / 5xx: Server Error
    if (statusCode != null && statusCode >= 500) {
      return ServerException(
        message: message != 'Unable to connect to YumSure backend'
            ? message
            : 'YumSure backend encountered an internal server error (HTTP $statusCode).',
        statusCode: statusCode,
        rawData: data,
      );
    }

    // Network / Socket / Timeout Failure
    if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.receiveTimeout ||
        error.type == DioExceptionType.sendTimeout ||
        error.type == DioExceptionType.connectionError) {
      return const NetworkException(
        message: 'Could not reach YumSure server. Please verify the backend is running and the device has network connectivity.',
      );
    }

    return ApiException(
      message: message,
      statusCode: statusCode,
      errorType: errorType,
      rawData: data,
    );
  }
}
