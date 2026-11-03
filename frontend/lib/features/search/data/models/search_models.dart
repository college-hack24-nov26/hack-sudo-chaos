import 'package:flutter/material.dart';

/// Nutrition badge model representing product intelligence indicators
class NutritionBadgeItem {
  final String label;
  final String severity; // 'HIGH', 'MODERATE', 'GOOD', 'NEUTRAL'

  const NutritionBadgeItem({
    required this.label,
    required this.severity,
  });

  factory NutritionBadgeItem.fromJson(Map<String, dynamic> json) {
    return NutritionBadgeItem(
      label: json['label']?.toString() ?? json['text']?.toString() ?? '',
      severity: (json['severity']?.toString() ?? 'NEUTRAL').toUpperCase(),
    );
  }

  Color get backgroundColor {
    switch (severity) {
      case 'HIGH':
        return const Color(0xFFFDE8E8);
      case 'MODERATE':
        return const Color(0xFFFFF1DE);
      case 'GOOD':
      case 'LOW':
        return const Color(0xFFE5F6EB);
      case 'NEUTRAL':
      default:
        return const Color(0xFFEFECE9);
    }
  }

  Color get textColor {
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
        return const Color(0xFF635E66);
    }
  }

  IconData? get icon {
    switch (severity) {
      case 'HIGH':
        return Icons.error_rounded;
      case 'MODERATE':
        return Icons.warning_rounded;
      case 'GOOD':
      case 'LOW':
        return Icons.check_circle_rounded;
      case 'NEUTRAL':
      default:
        return null;
    }
  }
}

/// Search result model for matching products
class SearchResultItem {
  final String barcode;
  final String productName;
  final String? brandName;
  final String category;
  final String? subCategory;
  final String? imageUrl;
  final List<NutritionBadgeItem> badges;

  const SearchResultItem({
    required this.barcode,
    required this.productName,
    this.brandName,
    required this.category,
    this.subCategory,
    this.imageUrl,
    this.badges = const [],
  });

  factory SearchResultItem.fromJson(Map<String, dynamic> json) {
    final rawBadges = json['badges'];
    List<NutritionBadgeItem> badgeList = [];
    if (rawBadges is List) {
      badgeList = rawBadges
          .whereType<Map<String, dynamic>>()
          .map((b) => NutritionBadgeItem.fromJson(b))
          .toList();
    } else if (json['key_finding'] != null) {
      badgeList.add(
        NutritionBadgeItem(
          label: json['key_finding'].toString(),
          severity: json['key_finding_severity']?.toString() ?? 'MODERATE',
        ),
      );
    }

    return SearchResultItem(
      barcode: json['barcode']?.toString() ?? '',
      productName: json['product_name']?.toString() ?? json['name']?.toString() ?? 'Unknown Product',
      brandName: json['brand_name']?.toString() ?? json['brand']?.toString(),
      category: json['food_category']?.toString() ?? json['category']?.toString() ?? 'Food',
      subCategory: json['sub_category']?.toString(),
      imageUrl: json['image_url']?.toString(),
      badges: badgeList,
    );
  }

  String get subtitleFormatted {
    if (brandName != null && brandName!.trim().isNotEmpty) {
      return '$category • $brandName';
    }
    if (subCategory != null && subCategory!.trim().isNotEmpty) {
      return '$category • $subCategory';
    }
    return category;
  }
}

/// Trending product item for discovery carousel
class TrendingProductItem {
  final String barcode;
  final String productName;
  final String category;
  final String? imageUrl;
  final NutritionBadgeItem? badge;

  const TrendingProductItem({
    required this.barcode,
    required this.productName,
    required this.category,
    this.imageUrl,
    this.badge,
  });

  factory TrendingProductItem.fromJson(Map<String, dynamic> json) {
    NutritionBadgeItem? badgeItem;
    if (json['badge'] is Map<String, dynamic>) {
      badgeItem = NutritionBadgeItem.fromJson(json['badge'] as Map<String, dynamic>);
    } else if (json['key_finding'] != null) {
      badgeItem = NutritionBadgeItem(
        label: json['key_finding'].toString(),
        severity: json['key_finding_severity']?.toString() ?? 'GOOD',
      );
    }

    return TrendingProductItem(
      barcode: json['barcode']?.toString() ?? '',
      productName: json['product_name']?.toString() ?? json['name']?.toString() ?? '',
      category: json['food_category']?.toString() ?? json['category']?.toString() ?? 'Snacks',
      imageUrl: json['image_url']?.toString(),
      badge: badgeItem,
    );
  }
}

/// Popular search chip item
class PopularSearchItem {
  final String query;
  final bool isHot;

  const PopularSearchItem({
    required this.query,
    this.isHot = false,
  });
}

/// Category filter capsule item
class CategoryFilterItem {
  final String id;
  final String label;
  final IconData icon;

  const CategoryFilterItem({
    required this.id,
    required this.label,
    required this.icon,
  });
}

