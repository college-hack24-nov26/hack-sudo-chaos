import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class ScannerBottomSheetPanel extends StatelessWidget {
  final VoidCallback onManualBarcodeTap;
  final VoidCallback onSearchTap;

  const ScannerBottomSheetPanel({
    super.key,
    required this.onManualBarcodeTap,
    required this.onSearchTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.fromLTRB(20.0, 12.0, 20.0, 20.0),
      decoration: const BoxDecoration(
        borderRadius: BorderRadius.vertical(top: Radius.circular(32.0)),
        gradient: LinearGradient(
          begin: Alignment.bottomLeft,
          end: Alignment.topRight,
          colors: [
            Color(0xFFFAF6F2), // Warm ivory bottom-left
            Color(0xFFF4EFF8), // Soft lavender tint
            Color(0xFFEFE9F5), // Top-right luminous lavender
          ],
          stops: [0.0, 0.55, 1.0],
        ),
        border: Border(
          top: BorderSide(color: Colors.white, width: 1.5),
          left: BorderSide(color: Colors.white, width: 1.0),
          right: BorderSide(color: Colors.white, width: 1.0),
        ),
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
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // 1. Centered Drag Handle (42x4.5, radius 3, #C4BDCB)
          Center(
            child: Container(
              width: 42.0,
              height: 4.5,
              decoration: BoxDecoration(
                color: const Color(0xFFC4BDCB),
                borderRadius: BorderRadius.circular(3.0),
              ),
            ),
          ),
          const SizedBox(height: 14.0),

          // 2. Section Heading: "Other Options"
          const Text(
            'Other Options',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 16.5,
              fontWeight: FontWeight.w800,
              color: Color(0xFF161616),
              letterSpacing: -0.2,
            ),
          ),
          const SizedBox(height: 12.0),

          // 3. Two Action Cards (Row with 12px gap)
          Row(
            children: [
              // Card 1: Enter Barcode Manually
              Expanded(
                child: _buildActionCard(
                  onTap: onManualBarcodeTap,
                  backgroundColor: const Color(0xFFF8F4F1),
                  icon: Icons.edit_outlined,
                  iconSize: 20.0,
                  primaryText: 'Enter Barcode',
                  secondaryText: 'Manually',
                ),
              ),
              const SizedBox(width: 12.0),

              // Card 2: Search Product by Name
              Expanded(
                child: _buildActionCard(
                  onTap: onSearchTap,
                  backgroundColor: const Color(0xFFF4EFF8),
                  icon: Icons.search_rounded,
                  iconSize: 21.0,
                  primaryText: 'Search Product',
                  secondaryText: 'by Name',
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard({
    required VoidCallback onTap,
    required Color backgroundColor,
    required IconData icon,
    required double iconSize,
    required String primaryText,
    required String secondaryText,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20.0),
        child: Container(
          height: 72.0,
          padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 8.0),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(20.0),
            border: Border.all(color: Colors.white, width: 1.5),
            boxShadow: const [
              BoxShadow(
                color: Color(0x0C000000),
                blurRadius: 10.0,
                offset: Offset(0, 3),
              ),
            ],
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // 42x42 Circular Icon Container
              Container(
                width: 42.0,
                height: 42.0,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Color(0xFFFDFBF9),
                  boxShadow: [
                    BoxShadow(
                      color: Color(0x0A000000),
                      blurRadius: 6.0,
                      offset: Offset(0, 2),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: Icon(
                  icon,
                  size: iconSize,
                  color: const Color(0xFF181818),
                ),
              ),
              const SizedBox(width: 10.0),

              // Text Stack
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      primaryText,
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 13.0,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF161616),
                        letterSpacing: -0.2,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 1.5),
                    Text(
                      secondaryText,
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 12.0,
                        fontWeight: FontWeight.w400,
                        color: Color(0xFF3A3540),
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
