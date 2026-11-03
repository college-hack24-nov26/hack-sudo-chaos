import 'package:flutter/material.dart';

/// Centralized Spacing and Layout Constants
class AppSpacing {
  AppSpacing._();

  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 12.0;
  static const double lg = 16.0;
  static const double xl = 20.0;
  static const double xxl = 24.0;
  static const double xxxl = 32.0;

  // Screen Padding
  static const EdgeInsets screenPadding = EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0);
  static const EdgeInsets cardPadding = EdgeInsets.all(16.0);
  static const EdgeInsets compactCardPadding = EdgeInsets.all(12.0);

  // Border Radii
  static const double radiusSm = 8.0;
  static const double radiusMd = 12.0;
  static const double radiusLg = 18.0;
  static const double radiusXl = 22.0;
  static const double radiusPill = 999.0;

  static const BorderRadius borderRadiusCard = BorderRadius.all(Radius.circular(radiusLg));
  static const BorderRadius borderRadiusPill = BorderRadius.all(Radius.circular(radiusPill));
  static const BorderRadius borderRadiusSm = BorderRadius.all(Radius.circular(radiusSm));
  static const BorderRadius borderRadiusMd = BorderRadius.all(Radius.circular(radiusMd));

  // Icon Sizes
  static const double iconSm = 16.0;
  static const double iconMd = 20.0;
  static const double iconLg = 24.0;
  static const double iconXl = 32.0;
}

