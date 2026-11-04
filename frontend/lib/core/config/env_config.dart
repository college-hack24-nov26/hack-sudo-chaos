import 'dart:io';
import 'package:flutter/foundation.dart';

/// Central Environment Configuration
/// Gracefully handles:
/// 1. Custom override via --dart-define=API_BASE_URL=http://<IP>:8000
/// 2. Custom host override via --dart-define=API_HOST=<IP>
/// 3. Physical Android device via USB + ADB reverse (http://127.0.0.1:8000)
/// 4. Physical Android device via Wi-Fi LAN
/// 5. Android Studio Emulator loopback (10.0.2.2:8000)
/// 6. Web & Desktop localhost (127.0.0.1:8000)
class EnvConfig {
  EnvConfig._();

  static const String _emulatorHost = '10.0.2.2'; // Standard Android emulator loopback to host
  static const int defaultPort = 8000;

  static String get baseUrl {
    // 1. Explicit full URL override (e.g. --dart-define=API_BASE_URL=http://192.168.1.146:8000)
    const String customBaseUrl = String.fromEnvironment('API_BASE_URL');
    if (customBaseUrl.isNotEmpty) {
      return customBaseUrl.endsWith('/')
          ? customBaseUrl.substring(0, customBaseUrl.length - 1)
          : customBaseUrl;
    }

    // 2. Custom IP/Host override (e.g. --dart-define=API_HOST=192.168.1.146)
    const String customHost = String.fromEnvironment('API_HOST');
    if (customHost.isNotEmpty) {
      return 'http://$customHost:$defaultPort';
    }

    // 3. Web
    if (kIsWeb) {
      return 'http://localhost:$defaultPort';
    }

    // 4. Android
    if (Platform.isAndroid) {
      // If user enabled adb reverse (adb reverse tcp:8000 tcp:8000), loopback 127.0.0.1 reaches host PC
      const bool useAdbReverse = bool.fromEnvironment('USE_ADB_REVERSE', defaultValue: false);
      if (useAdbReverse) {
        return 'http://127.0.0.1:$defaultPort';
      }

      // Default: Emulator loopback. For physical device, pass --dart-define=API_BASE_URL=...
      return 'http://$_emulatorHost:$defaultPort';
    }

    // 5. Default for iOS Simulator, macOS, Windows Desktop
    return 'http://127.0.0.1:$defaultPort';
  }

  static const Duration connectTimeout = Duration(seconds: 8);
  static const Duration receiveTimeout = Duration(seconds: 10);
}
