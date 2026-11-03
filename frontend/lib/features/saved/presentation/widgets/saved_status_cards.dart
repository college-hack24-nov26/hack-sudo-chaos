import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

class SavedEmptyCard extends StatelessWidget {
  final VoidCallback onScanProduct;

  const SavedEmptyCard({super.key, required this.onScanProduct});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 24.0),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 10.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Column(
        children: [
          Container(
            width: 48.0,
            height: 48.0,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: Color(0xFFF3EDFA),
            ),
            alignment: Alignment.center,
            child: const Icon(
              Icons.bookmark_border_rounded,
              size: 26.0,
              color: Color(0xFF8C6FE6),
            ),
          ),
          const SizedBox(height: 12.0),
          const Text(
            'No saved products yet',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 15.0,
              fontWeight: FontWeight.w800,
              color: Color(0xFF141414),
            ),
          ),
          const SizedBox(height: 4.0),
          const Text(
            'Scan or search a food product and tap the bookmark ribbon to save it here for quick nutrition insights.',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 12.0,
              color: Color(0xFF6E6877),
              height: 1.35,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16.0),
          OutlinedButton.icon(
            onPressed: onScanProduct,
            icon: const Icon(Icons.qr_code_scanner_rounded, size: 16.0),
            label: const Text(
              'Scan a Product',
              style: TextStyle(
                fontFamily: AppTypography.fontFamily,
                fontSize: 12.5,
                fontWeight: FontWeight.w700,
              ),
            ),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF141414),
              side: const BorderSide(color: Color(0xFFE2DAD2), width: 1.0),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12.0)),
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            ),
          ),
        ],
      ),
    );
  }
}

class SavedOfflineCard extends StatelessWidget {
  final VoidCallback onRetry;

  const SavedOfflineCard({super.key, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFBF8F6),
        borderRadius: BorderRadius.circular(22.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 10.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(
            Icons.wifi_off_rounded,
            size: 16.0,
            color: Color(0xFF8E8A93),
          ),
          const SizedBox(width: 10.0),
          const Expanded(
            child: Text(
              'Saved products offline',
              style: TextStyle(
                fontFamily: AppTypography.fontFamily,
                fontSize: 12.0,
                fontWeight: FontWeight.w500,
                color: Color(0xFF6E6877),
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onRetry,
              borderRadius: BorderRadius.circular(8.0),
              child: const Padding(
                padding: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.refresh_rounded, size: 14.0, color: AppColors.brandOrange),
                    SizedBox(width: 3.0),
                    Text(
                      'Retry',
                      style: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 12.0,
                        fontWeight: FontWeight.w700,
                        color: AppColors.brandOrange,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

