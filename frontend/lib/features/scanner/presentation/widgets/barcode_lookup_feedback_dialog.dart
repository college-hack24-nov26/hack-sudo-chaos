import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';

enum ScannerFeedbackType {
  notFound,
  offline,
  invalid,
}

class BarcodeLookupFeedbackSheet extends StatelessWidget {
  final String barcode;
  final ScannerFeedbackType feedbackType;
  final VoidCallback onScanAgain;
  final VoidCallback? onRetry;
  final VoidCallback? onEnterManually;

  const BarcodeLookupFeedbackSheet({
    super.key,
    required this.barcode,
    required this.feedbackType,
    required this.onScanAgain,
    this.onRetry,
    this.onEnterManually,
  });

  static Future<void> show(
    BuildContext context, {
    required String barcode,
    required ScannerFeedbackType feedbackType,
    required VoidCallback onScanAgain,
    VoidCallback? onRetry,
    VoidCallback? onEnterManually,
  }) {
    return showModalBottomSheet(
      context: context,
      isDismissible: false,
      enableDrag: false,
      backgroundColor: Colors.transparent,
      builder: (ctx) => BarcodeLookupFeedbackSheet(
        barcode: barcode,
        feedbackType: feedbackType,
        onScanAgain: () {
          Navigator.of(ctx).pop();
          onScanAgain();
        },
        onRetry: onRetry != null
            ? () {
                Navigator.of(ctx).pop();
                onRetry();
              }
            : null,
        onEnterManually: onEnterManually != null
            ? () {
                Navigator.of(ctx).pop();
                onEnterManually();
              }
            : null,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color iconColor;
    Color iconBg;
    String title;
    String message;

    switch (feedbackType) {
      case ScannerFeedbackType.notFound:
        icon = Icons.inventory_2_outlined;
        iconColor = const Color(0xFFF05442);
        iconBg = const Color(0xFFFDE2DA);
        title = 'Product Not Found';
        message = 'We could not find nutritional data for barcode "$barcode" in our verified database or Open Food Facts.';
        break;
      case ScannerFeedbackType.offline:
        icon = Icons.wifi_off_rounded;
        iconColor = const Color(0xFFE57E24);
        iconBg = const Color(0xFFFFF1DE);
        title = 'Backend Unreachable';
        message = 'Could not reach the YumSure intelligence service to evaluate barcode "$barcode". Please verify your connection.';
        break;
      case ScannerFeedbackType.invalid:
        icon = Icons.error_outline_rounded;
        iconColor = const Color(0xFFE53935);
        iconBg = const Color(0xFFFFECEB);
        title = 'Invalid Barcode Format';
        message = 'The scanned barcode code "$barcode" is not a standard retail food format (EAN-13, EAN-8, or UPC-A).';
        break;
    }

    return Container(
      padding: const EdgeInsets.fromLTRB(24.0, 20.0, 24.0, 28.0),
      decoration: const BoxDecoration(
        color: Color(0xFFFAF7F5),
        borderRadius: BorderRadius.vertical(top: Radius.circular(30.0)),
        border: Border(top: BorderSide(color: Colors.white, width: 1.5)),
        boxShadow: [
          BoxShadow(
            color: Color(0x33000000),
            blurRadius: 24.0,
            offset: Offset(0, -6),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Icon badge
          Container(
            width: 52.0,
            height: 52.0,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: iconBg,
            ),
            alignment: Alignment.center,
            child: Icon(icon, size: 26.0, color: iconColor),
          ),
          const SizedBox(height: 14.0),

          // Title
          Text(
            title,
            style: const TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 18.0,
              fontWeight: FontWeight.w800,
              color: Color(0xFF141414),
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6.0),

          // Message
          Text(
            message,
            style: const TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 12.5,
              color: Color(0xFF5A5560),
              height: 1.38,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 22.0),

          // Action Buttons
          if (feedbackType == ScannerFeedbackType.offline && onRetry != null) ...[
            ElevatedButton(
              onPressed: onRetry,
              style: ElevatedButton.styleFrom(
                backgroundColor: AppColors.brandOrange,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16.0)),
                minimumSize: const Size(double.infinity, 48.0),
                elevation: 0,
              ),
              child: const Text(
                'Retry Connection',
                style: TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: 14.0,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
            const SizedBox(height: 10.0),
          ],

          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: onScanAgain,
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF141414),
                    side: const BorderSide(color: Color(0xFFDCD5CE), width: 1.2),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16.0)),
                    minimumSize: const Size(0, 48.0),
                  ),
                  child: const Text(
                    'Scan Again',
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 13.5,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              if (onEnterManually != null) ...[
                const SizedBox(width: 10.0),
                Expanded(
                  child: ElevatedButton(
                    onPressed: onEnterManually,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF1D1C24),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16.0)),
                      minimumSize: const Size(0, 48.0),
                      elevation: 0,
                    ),
                    child: const Text(
                      'Enter Manually',
                      style: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 13.5,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }
}

