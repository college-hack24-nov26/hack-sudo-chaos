import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/home_models.dart';

class ScanInsightsSection extends StatelessWidget {
  final ScanInsight? insight;
  final Object? error;
  final String selectedTimeframe;
  final ValueChanged<String> onTimeframeChanged;
  final VoidCallback onScanProduct;
  final VoidCallback? onInsightTapped;
  final VoidCallback? onRetry;

  const ScanInsightsSection({
    super.key,
    required this.insight,
    this.error,
    required this.selectedTimeframe,
    required this.onTimeframeChanged,
    required this.onScanProduct,
    this.onInsightTapped,
    this.onRetry,
  });

  String _formatTimeframeLabel(String tf) {
    switch (tf) {
      case '30d':
        return 'Last 30 days';
      case 'all':
        return 'All time';
      case '7d':
      default:
        return 'Last 7 days';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section Header Row with Timeframe Selector
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const Text(
                'Your Scan Insights',
                style: TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: 16.0,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF141414),
                  letterSpacing: -0.2,
                ),
              ),
              PopupMenuButton<String>(
                initialValue: selectedTimeframe,
                onSelected: onTimeframeChanged,
                color: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12.0),
                  side: const BorderSide(color: AppColors.border),
                ),
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20.0),
                    border: Border.all(color: const Color(0xFFE8E2DC), width: 0.8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _formatTimeframeLabel(selectedTimeframe),
                        style: const TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 11.5,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF141414),
                        ),
                      ),
                      const SizedBox(width: 3.0),
                      const Icon(
                        Icons.keyboard_arrow_down_rounded,
                        size: 16.0,
                        color: Color(0xFF141414),
                      ),
                    ],
                  ),
                ),
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: '7d',
                    child: Text('Last 7 days', style: TextStyle(fontSize: 12.0)),
                  ),
                  const PopupMenuItem(
                    value: '30d',
                    child: Text('Last 30 days', style: TextStyle(fontSize: 12.0)),
                  ),
                  const PopupMenuItem(
                    value: 'all',
                    child: Text('All time', style: TextStyle(fontSize: 12.0)),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12.0),

        // Body: Height 84.0 card with radius 24, #FFF9F6 background + pink curve, 48x48 icon box
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0),
          child: _buildContent(),
        ),
      ],
    );
  }

  Widget _buildContent() {
    if (error != null) {
      return _EditorialInsightBanner(
        title: 'Insights Offline',
        subtitle: 'Connect backend for nutritional trends',
        isError: true,
        onAction: onRetry,
      );
    }

    if (insight != null) {
      return _EditorialInsightBanner(
        title: insight!.title,
        subtitle: insight!.description,
        isError: false,
        onAction: onInsightTapped,
      );
    }

    // HTTP 200 with null: First-use state in the same 84dp card geometry
    return _EditorialInsightBanner(
      title: 'No Insights Yet',
      subtitle: 'Scan products to uncover nutritional habits',
      isError: false,
      onAction: onScanProduct,
    );
  }
}

/// Editorial Insight Banner with exact reference geometry:
/// - Height: 84.0
/// - BorderRadius: 24.0
/// - Fill: #FFF9F6 with soft pink curved wave #FFE5DF in bottom-right
/// - Border: 1.5px #FFFFFF
/// - Shadow: blurRadius 14, offset (0, 6)
/// - Left icon box: 48x48, radius 14, #FDE2DA with 3 vertical bars + 1 dot in #F05442
/// - Right button: 34x34 white circle with #181818 icon
class _EditorialInsightBanner extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool isError;
  final VoidCallback? onAction;

  const _EditorialInsightBanner({
    required this.title,
    required this.subtitle,
    required this.isError,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 84.0,
      decoration: BoxDecoration(
        color: const Color(0xFFFFF9F6),
        borderRadius: BorderRadius.circular(24.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D000000),
            blurRadius: 14.0,
            offset: Offset(0, 6),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          // Bottom-Right Soft Pink Curved Wave (#FFE5DF)
          const Positioned.fill(
            child: CustomPaint(
              painter: _InsightBackgroundWavePainter(),
            ),
          ),

          // Content Row
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: onAction,
              borderRadius: BorderRadius.circular(24.0),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Row(
                  children: [
                    // Left Icon Box (48x48, radius 14, fill #FDE2DA)
                    Container(
                      width: 48.0,
                      height: 48.0,
                      decoration: BoxDecoration(
                        color: const Color(0xFFFDE2DA),
                        borderRadius: BorderRadius.circular(14.0),
                      ),
                      alignment: Alignment.center,
                      child: const CustomPaint(
                        size: Size(32.0, 24.0),
                        painter: _InsightChartIconPainter(),
                      ),
                    ),
                    const SizedBox(width: 14.0),

                    // Title & Subtitle
                    Expanded(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            title,
                            style: const TextStyle(
                              fontFamily: AppTypography.fontFamily,
                              fontSize: 14.5,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF141414),
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 3.0),
                          Text(
                            subtitle,
                            style: const TextStyle(
                              fontFamily: AppTypography.fontFamily,
                              fontSize: 11.5,
                              color: Color(0xFF6E6877),
                              height: 1.3,
                            ),
                            maxLines: 2,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 10.0),

                    // Right Button (34x34 white circle with #181818 icon)
                    Container(
                      width: 34.0,
                      height: 34.0,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        shape: BoxShape.circle,
                        border: Border.all(color: const Color(0xFFEFE6DF), width: 1.0),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x0A000000),
                            blurRadius: 6.0,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      alignment: Alignment.center,
                      child: Icon(
                        isError ? Icons.refresh_rounded : Icons.arrow_forward_rounded,
                        size: 16.0,
                        color: const Color(0xFF181818),
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

/// Soft pink curved wave in bottom-right corner (#FFE5DF)
class _InsightBackgroundWavePainter extends CustomPainter {
  const _InsightBackgroundWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final wavePaint = Paint()
      ..color = const Color(0xFFFFE5DF)
      ..style = PaintingStyle.fill;

    final path = Path()
      ..moveTo(size.width * 0.70, size.height)
      ..quadraticBezierTo(
        size.width * 0.82,
        size.height * 0.25,
        size.width,
        size.height * 0.15,
      )
      ..lineTo(size.width, size.height)
      ..close();

    canvas.drawPath(path, wavePaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// 3 vertical bars + 1 dot in #F05442
class _InsightChartIconPainter extends CustomPainter {
  const _InsightChartIconPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFF05442)
      ..style = PaintingStyle.fill;

    // Bar 1 (short)
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(2.0, size.height - 10.0, 3.5, 10.0),
        const Radius.circular(1.5),
      ),
      paint,
    );

    // Bar 2 (tall)
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(9.0, size.height - 20.0, 3.5, 20.0),
        const Radius.circular(1.5),
      ),
      paint,
    );

    // Bar 3 (medium)
    canvas.drawRRect(
      RRect.fromRectAndRadius(
        Rect.fromLTWH(16.0, size.height - 15.0, 3.5, 15.0),
        const Radius.circular(1.5),
      ),
      paint,
    );

    // Dot at top-right
    canvas.drawCircle(Offset(size.width - 5.0, 5.0), 2.5, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
