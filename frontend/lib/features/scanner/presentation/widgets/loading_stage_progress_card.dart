import 'dart:math' as math;
import 'package:flutter/material.dart';

enum LoadingStage {
  readingBarcode,
  fetchingData,
  processingNutrition,
  preparingInsights,
  completed,
}

class LoadingStageProgressCard extends StatefulWidget {
  final LoadingStage currentStage;

  const LoadingStageProgressCard({
    super.key,
    required this.currentStage,
  });

  @override
  State<LoadingStageProgressCard> createState() => _LoadingStageProgressCardState();
}

class _LoadingStageProgressCardState extends State<LoadingStageProgressCard>
    with SingleTickerProviderStateMixin {
  late final AnimationController _spinnerController;

  @override
  void initState() {
    super.initState();
    _spinnerController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    )..repeat();
  }

  @override
  void dispose() {
    _spinnerController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const stages = [
      _StageInfo('Reading barcode', LoadingStage.readingBarcode),
      _StageInfo('Fetching product data', LoadingStage.fetchingData),
      _StageInfo('Processing nutrition info', LoadingStage.processingNutrition),
      _StageInfo('Preparing insights', LoadingStage.preparingInsights),
    ];

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24.0),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 18.0),
        decoration: BoxDecoration(
          color: const Color(0xFFFAF8FA),
          borderRadius: BorderRadius.circular(24.0),
          border: Border.all(color: Colors.white, width: 1.5),
          boxShadow: const [
            BoxShadow(
              color: Color(0x0B000000),
              blurRadius: 18.0,
              offset: Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          children: List.generate(stages.length, (index) {
            final info = stages[index];
            final state = _resolveState(info.stage, widget.currentStage);
            final isLast = index == stages.length - 1;

            return _buildTimelineRow(
              label: info.label,
              state: state,
              isLast: isLast,
            );
          }),
        ),
      ),
    );
  }

  _RowState _resolveState(LoadingStage stage, LoadingStage current) {
    if (current == LoadingStage.completed) {
      return _RowState.completed;
    }
    if (stage.index < current.index) {
      return _RowState.completed;
    } else if (stage.index == current.index) {
      return _RowState.processing;
    } else {
      return _RowState.pending;
    }
  }

  Widget _buildTimelineRow({
    required String label,
    required _RowState state,
    required bool isLast,
  }) {
    if (state == _RowState.processing) {
      return Container(
        height: 44.0,
        margin: const EdgeInsets.symmetric(vertical: 4.0),
        padding: const EdgeInsets.symmetric(horizontal: 12.0),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(22.0),
          gradient: const LinearGradient(
            begin: Alignment.centerLeft,
            end: Alignment.centerRight,
            colors: [
              Color(0xFFEFE9FE),
              Color(0xFFE8DFFE),
            ],
          ),
        ),
        child: Row(
          children: [
            // Custom dotted circular spinner
            RotationTransition(
              turns: _spinnerController,
              child: const CustomPaint(
                size: Size(24.0, 24.0),
                painter: _DottedSpinnerPainter(),
              ),
            ),
            const SizedBox(width: 14.0),
            Text(
              label,
              style: const TextStyle(
                fontFamily: 'Manrope',
                fontSize: 14.5,
                fontWeight: FontWeight.w800,
                color: Color(0xFF161426),
              ),
            ),
          ],
        ),
      );
    }

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Left Timeline Indicator Column
          SizedBox(
            width: 24.0,
            child: Column(
              children: [
                if (state == _RowState.completed)
                  Container(
                    width: 24.0,
                    height: 24.0,
                    decoration: const BoxDecoration(
                      color: Color(0xFF22C55E),
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: const Icon(
                      Icons.check_rounded,
                      size: 15.0,
                      color: Colors.white,
                    ),
                  )
                else
                  Container(
                    width: 22.0,
                    height: 22.0,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: const Color(0xFFD0CCD8),
                        width: 1.8,
                      ),
                    ),
                  ),

                // Connecting Timeline Line
                if (!isLast)
                  Expanded(
                    child: Container(
                      width: 1.5,
                      color: const Color(0xFFE2DEE8),
                      margin: const EdgeInsets.symmetric(vertical: 3.0),
                    ),
                  ),
              ],
            ),
          ),

          const SizedBox(width: 14.0),

          // Right Label & Divider
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 10.0),
                  child: Text(
                    label,
                    style: TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 14.0,
                      fontWeight: state == _RowState.completed ? FontWeight.w600 : FontWeight.w500,
                      color: state == _RowState.completed
                          ? const Color(0xFF2A2836)
                          : const Color(0xFF3A3744),
                    ),
                  ),
                ),
                if (!isLast)
                  const Divider(
                    height: 1.0,
                    thickness: 1.0,
                    color: Color(0xFFF0EDF5),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

enum _RowState { completed, processing, pending }

class _StageInfo {
  final String label;
  final LoadingStage stage;
  const _StageInfo(this.label, this.stage);
}

class _DottedSpinnerPainter extends CustomPainter {
  const _DottedSpinnerPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 2.5;
    const dotCount = 8;
    const dotRadius = 2.2;

    for (int i = 0; i < dotCount; i++) {
      final angle = i * (2 * math.pi / dotCount);
      final x = center.dx + radius * math.cos(angle);
      final y = center.dy + radius * math.sin(angle);
      final opacity = ((i + 1) / dotCount).clamp(0.2, 1.0);

      final paint = Paint()
        ..color = const Color(0xFF6E44FF).withValues(alpha: opacity)
        ..style = PaintingStyle.fill;

      canvas.drawCircle(Offset(x, y), dotRadius, paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

