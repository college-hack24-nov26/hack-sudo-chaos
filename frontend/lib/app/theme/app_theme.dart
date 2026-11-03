import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app_colors.dart';
import 'app_spacing.dart';
import 'app_typography.dart';

class AppTheme {
  AppTheme._();

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: AppColors.background,
      fontFamily: AppTypography.fontFamily,
      colorScheme: const ColorScheme.light(
        primary: AppColors.accentDark,
        secondary: AppColors.brandOrange,
        surface: AppColors.surface,
        error: AppColors.concern,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: AppColors.textPrimary,
        onError: Colors.white,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        systemOverlayStyle: SystemUiOverlayStyle.dark,
        iconTheme: IconThemeData(color: AppColors.textPrimary),
      ),
      cardTheme: const CardThemeData(
        color: AppColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: AppSpacing.borderRadiusCard,
          side: BorderSide(color: AppColors.border, width: 1.0),
        ),
        margin: EdgeInsets.zero,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.accentDark,
          foregroundColor: Colors.white,
          elevation: 0,
          shape: const RoundedRectangleBorder(
            borderRadius: AppSpacing.borderRadiusPill,
          ),
          textStyle: AppTypography.label.copyWith(color: Colors.white),
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: AppColors.divider,
        thickness: 1,
        space: 1,
      ),
    );
  }
}
