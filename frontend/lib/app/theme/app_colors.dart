import 'package:flutter/material.dart';

/// Centralized Design Token System for YumSure
/// Follows the warm cream, soft peach, and lavender aesthetic without heavy glassmorphism.
class AppColors {
  AppColors._();

  // Backgrounds & Surfaces
  static const Color background = Color(0xFFFBF8F5); // Warm cream / ivory
  static const Color backgroundGradientEnd = Color(0xFFF4ECE4);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceSubtle = Color(0xFFF7F3EE);
  static const Color surfaceCard = Color(0xFFFFFFFF);

  // Text Colors
  static const Color textPrimary = Color(0xFF191B1F); // Dark navy / almost black
  static const Color textSecondary = Color(0xFF6B7280); // Neutral slate
  static const Color textTertiary = Color(0xFF9CA3AF);
  static const Color textInverse = Color(0xFFFFFFFF);

  // Brand & Accents
  static const Color brandOrange = Color(0xFFFF7A45); // YumSure logo smile
  static const Color accentPeach = Color(0xFFFFD8CC);
  static const Color accentPeachLight = Color(0xFFFFF1EB);
  static const Color accentLavender = Color(0xFFE8DEF8);
  static const Color accentLavenderLight = Color(0xFFF5EEFD);
  static const Color accentPurple = Color(0xFF7C3AED);
  static const Color accentDark = Color(0xFF1E222B); // Dark navy pill buttons

  // Interpretation & Status Colors (Consistent across all screens)
  static const Color positive = Color(0xFF16A34A); // Green - Good / Low concern
  static const Color positiveBackground = Color(0xFFDCFCE7);
  static const Color positiveBorder = Color(0xFF86EFAC);

  static const Color moderate = Color(0xFFF59E0B); // Amber - Medium / Caution
  static const Color moderateBackground = Color(0xFFFEF3C7);
  static const Color moderateBorder = Color(0xFFFCD34D);

  static const Color concern = Color(0xFFEF4444); // Red - High concern / Alert
  static const Color concernBackground = Color(0xFFFEE2E2);
  static const Color concernBorder = Color(0xFFFCA5A5);

  static const Color neutral = Color(0xFF3B82F6); // Blue - Informational
  static const Color neutralBackground = Color(0xFFDBEAFE);
  static const Color neutralBorder = Color(0xFF93C5FD);

  static const Color unclassified = Color(0xFF64748B);
  static const Color unclassifiedBackground = Color(0xFFF1F5F9);

  // Specific Functional Nutrient Colors
  static const Color nutrientCarbs = Color(0xFF0EA5E9);
  static const Color nutrientCarbsBg = Color(0xFFE0F2FE);
  static const Color nutrientFat = Color(0xFFF97316);
  static const Color nutrientFatBg = Color(0xFFFFEDD5);
  static const Color nutrientSugar = Color(0xFFF43F5E);
  static const Color nutrientSugarBg = Color(0xFFFFE4E6);
  static const Color nutrientProtein = Color(0xFF8B5CF6);
  static const Color nutrientProteinBg = Color(0xFFEDE9FE);
  static const Color nutrientSodium = Color(0xFF0284C7);
  static const Color nutrientSodiumBg = Color(0xFFE0F2FE);

  // Borders & Dividers
  static const Color border = Color(0xFFEFE8E1);
  static const Color borderSubtle = Color(0xFFF5EFE9);
  static const Color divider = Color(0xFFECE4DC);

  // Energy Hero Gradient (Lightweight static gradient)
  static const List<Color> energyGradient = [
    Color(0xFFE0E7FF), // Soft indigo
    Color(0xFFFFE4E6), // Soft peach
    Color(0xFFFEF3C7), // Soft yellow
  ];

  // AI Gradient
  static const List<Color> aiGradient = [
    Color(0xFFF5EEFD),
    Color(0xFFFFFFFF),
  ];
}

