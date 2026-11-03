import 'package:flutter/material.dart';
import 'app_colors.dart';

/// Centralized Typography Hierarchy powered by Manrope font
class AppTypography {
  AppTypography._();

  static const String fontFamily = 'Manrope';

  static const TextStyle display = TextStyle(
    fontFamily: fontFamily,
    fontSize: 28.0,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.5,
    height: 1.2,
  );

  static const TextStyle h1 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22.0,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.3,
    height: 1.25,
  );

  static const TextStyle h2 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 18.0,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
    letterSpacing: -0.2,
    height: 1.3,
  );

  static const TextStyle h3 = TextStyle(
    fontFamily: fontFamily,
    fontSize: 16.0,
    fontWeight: FontWeight.w600,
    color: AppColors.textPrimary,
    height: 1.35,
  );

  static const TextStyle bodyLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15.0,
    fontWeight: FontWeight.w400,
    color: AppColors.textPrimary,
    height: 1.4,
  );

  static const TextStyle bodyMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 13.5,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.4,
  );

  static const TextStyle bodySmall = TextStyle(
    fontFamily: fontFamily,
    fontSize: 12.0,
    fontWeight: FontWeight.w400,
    color: AppColors.textSecondary,
    height: 1.35,
  );

  static const TextStyle label = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11.5,
    fontWeight: FontWeight.w600,
    letterSpacing: 0.2,
    color: AppColors.textPrimary,
  );

  static const TextStyle badge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 11.0,
    fontWeight: FontWeight.w700,
    letterSpacing: 0.1,
  );

  static const TextStyle valueLarge = TextStyle(
    fontFamily: fontFamily,
    fontSize: 22.0,
    fontWeight: FontWeight.w800,
    color: AppColors.textPrimary,
    letterSpacing: -0.5,
  );

  static const TextStyle valueMedium = TextStyle(
    fontFamily: fontFamily,
    fontSize: 15.0,
    fontWeight: FontWeight.w700,
    color: AppColors.textPrimary,
  );
}

