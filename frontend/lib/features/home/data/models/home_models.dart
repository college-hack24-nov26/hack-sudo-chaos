import 'package:flutter/material.dart';

/// Represents a distinct scanned product record from scan history
class ScanHistoryItem {
  final String barcode;
  final String productName;
  final String? brandName;
  final String foodCategory;
  final String? imageUrl;
  final DateTime scannedAt;
  final String? keyFinding;
  final String? keyFindingSeverity; // 'HIGH', 'MODERATE', 'POSITIVE'

  const ScanHistoryItem({
    required this.barcode,
    required this.productName,
    this.brandName,
    required this.foodCategory,
    this.imageUrl,
    required this.scannedAt,
    this.keyFinding,
    this.keyFindingSeverity,
  });

  String get relativeTimeFormatted {
    final now = DateTime.now();
    final difference = now.difference(scannedAt);

    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} mins ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours} ${difference.inHours == 1 ? 'hour' : 'hours'} ago';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} ${difference.inDays == 1 ? 'day' : 'days'} ago';
    } else {
      final weeks = (difference.inDays / 7).floor();
      return '$weeks ${weeks == 1 ? 'week' : 'weeks'} ago';
    }
  }

  factory ScanHistoryItem.fromJson(Map<String, dynamic> json) {
    return ScanHistoryItem(
      barcode: json['barcode']?.toString() ?? '',
      productName: json['product_name']?.toString() ?? 'Packaged Product',
      brandName: json['brand_name']?.toString(),
      foodCategory: json['food_category']?.toString() ?? 'Packaged Food',
      imageUrl: json['image_url']?.toString(),
      scannedAt: json['scanned_at'] != null
          ? DateTime.tryParse(json['scanned_at'].toString()) ?? DateTime.now()
          : DateTime.now(),
      keyFinding: json['key_finding']?.toString(),
      keyFindingSeverity: json['key_finding_severity']?.toString() ?? 'MODERATE',
    );
  }
}

/// Represents an aggregated nutritional insight derived from scan records
class ScanInsight {
  final String title;
  final String description;
  final int affectedCount;
  final int totalScannedCount;
  final String findingType; // 'high_sodium', 'high_sugar', 'high_fat', 'balanced'
  final String timeframe; // '7d', '30d', 'all'

  const ScanInsight({
    required this.title,
    required this.description,
    required this.affectedCount,
    required this.totalScannedCount,
    required this.findingType,
    required this.timeframe,
  });

  factory ScanInsight.fromJson(Map<String, dynamic> json) {
    return ScanInsight(
      title: json['title']?.toString() ?? 'Nutritional Insight',
      description: json['description']?.toString() ?? '',
      affectedCount: json['affected_count'] as int? ?? 0,
      totalScannedCount: json['total_scanned_count'] as int? ?? 0,
      findingType: json['finding_type']?.toString() ?? 'general',
      timeframe: json['timeframe']?.toString() ?? '7d',
    );
  }
}

/// Category item for the Explore Categories section
class CategoryItem {
  final String id;
  final String title;
  final IconData icon;
  final List<Color> gradientColors;
  final String? assetImagePath;

  const CategoryItem({
    required this.id,
    required this.title,
    required this.icon,
    required this.gradientColors,
    this.assetImagePath,
  });
}

