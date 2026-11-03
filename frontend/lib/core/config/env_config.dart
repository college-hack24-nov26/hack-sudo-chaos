import 'dart:io';
import 'package:flutter/foundation.dart';

/// Central Environment Configuration
/// Gracefully handles Android Emulator (10.0.2.2) vs Physical Device / Web localhost
class EnvConfig {
  EnvConfig._();

  static const String _defaultHost = '10.0.2.2'; // Standard Android emulator loopback to host
  static const int defaultPort = 8000;

  static String get baseUrl {
    // If running in release or user specified override via dart-define
    const String customBaseUrl = String.fromEnvironment('API_BASE_URL');
    if (customBaseUrl.isNotEmpty) {
      return customBaseUrl;
    }

    if (kIsWeb) {
      return 'http://localhost:$defaultPort';
    }

    if (Platform.isAndroid) {
      // 10.0.2.2 is the special alias to host loopback interface in Android Studio emulator
      return 'http://$_defaultHost:$defaultPort';
    }

    // Default for iOS Simulator, macOS, Windows Desktop
    return 'http://127.0.0.1:$defaultPort';
  }

  static const Duration connectTimeout = Duration(seconds: 8);
  static const Duration receiveTimeout = Duration(seconds: 10);
}

