import 'package:flutter/material.dart';

class SavedNutritionBadge {
  final String label;
  final String severity; // 'HIGH', 'MODERATE', 'GOOD', 'NEUTRAL'

  const SavedNutritionBadge({
    required this.label,
    required this.severity,
  });

  Map<String, dynamic> toJson() => {
        'label': label,
        'severity': severity,
      };

  factory SavedNutritionBadge.fromJson(Map<String, dynamic> json) => SavedNutritionBadge(
        label: json['label']?.toString() ?? '',
        severity: (json['severity']?.toString() ?? 'NEUTRAL').toUpperCase(),
      );

  Color get backgroundColor {
    switch (severity) {
      case 'HIGH':
        return const Color(0xFFFDE6E6);
      case 'MODERATE':
        return const Color(0xFFFDEFD9);
      case 'GOOD':
      case 'LOW':
        return const Color(0xFFE3F5E8);
      case 'NEUTRAL':
      default:
        return const Color(0xFFEFECE9);
    }
  }

  Color get textColor {
    switch (severity) {
      case 'HIGH':
        return const Color(0xFFC92A2A);
      case 'MODERATE':
        return const Color(0xFFB8621B);
      case 'GOOD':
      case 'LOW':
        return const Color(0xFF1E7E34);
      case 'NEUTRAL':
      default:
        return const Color(0xFF635E66);
    }
  }

  Color get iconCircleColor {
    switch (severity) {
      case 'HIGH':
        return const Color(0xFFD9383A);
      case 'MODERATE':
        return const Color(0xFFD97E26);
      case 'GOOD':
      case 'LOW':
        return const Color(0xFF2B8A44);
      case 'NEUTRAL':
      default:
        return const Color(0xFF8E8A93);
    }
  }

  IconData? get icon {
    switch (severity) {
      case 'HIGH':
        return Icons.priority_high_rounded;
      case 'MODERATE':
        return Icons.warning_rounded;
      case 'GOOD':
      case 'LOW':
        return Icons.check_rounded;
      case 'NEUTRAL':
      default:
        return null;
    }
  }
}

class SavedProductItem {
  final String barcode;
  final String productName;
  final String category; // 'Snacks', 'Beverages', 'Biscuits', 'Dairy', etc.
  final String brandOrQuantity; // e.g. "Potato Chips • 100 g"
  final String? imageUrl;
  final DateTime savedAt;
  final List<SavedNutritionBadge> badges;

  const SavedProductItem({
    required this.barcode,
    required this.productName,
    required this.category,
    required this.brandOrQuantity,
    this.imageUrl,
    required this.savedAt,
    this.badges = const [],
  });

  Map<String, dynamic> toJson() => {
        'barcode': barcode,
        'product_name': productName,
        'category': category,
        'brand_or_quantity': brandOrQuantity,
        'image_url': imageUrl,
        'saved_at': savedAt.toIso8601String(),
        'badges': badges.map((b) => b.toJson()).toList(),
      };

  factory SavedProductItem.fromJson(Map<String, dynamic> json) {
    final rawBadges = json['badges'];
    List<SavedNutritionBadge> badgeList = [];
    if (rawBadges is List) {
      badgeList = rawBadges
          .whereType<Map<String, dynamic>>()
          .map((b) => SavedNutritionBadge.fromJson(b))
          .toList();
    }

    return SavedProductItem(
      barcode: json['barcode']?.toString() ?? '',
      productName: json['product_name']?.toString() ?? 'Product',
      category: json['category']?.toString() ?? 'Snacks',
      brandOrQuantity: json['brand_or_quantity']?.toString() ?? '',
      imageUrl: json['image_url']?.toString(),
      savedAt: json['saved_at'] != null
          ? DateTime.tryParse(json['saved_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
      badges: badgeList,
    );
  }
}

enum SavedSortOrder {
  recentlySaved,
  alphabetical,
}

