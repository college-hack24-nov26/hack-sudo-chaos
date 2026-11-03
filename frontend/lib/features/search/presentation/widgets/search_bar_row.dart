import 'dart:async';
import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';

class SearchBarRow extends StatefulWidget {
  final String initialQuery;
  final ValueChanged<String> onQueryChanged;
  final VoidCallback onBarcodeTap;

  const SearchBarRow({
    super.key,
    required this.initialQuery,
    required this.onQueryChanged,
    required this.onBarcodeTap,
  });

  @override
  State<SearchBarRow> createState() => _SearchBarRowState();
}

class _SearchBarRowState extends State<SearchBarRow> {
  late final TextEditingController _controller;
  Timer? _debounceTimer;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.initialQuery);
  }

  @override
  void didUpdateWidget(covariant SearchBarRow oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialQuery != oldWidget.initialQuery && widget.initialQuery != _controller.text) {
      _controller.text = widget.initialQuery;
    }
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  void _onTextChanged(String value) {
    setState(() {});
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 350), () {
      widget.onQueryChanged(value);
    });
  }

  void _onClear() {
    _controller.clear();
    setState(() {});
    _debounceTimer?.cancel();
    widget.onQueryChanged('');
  }

  @override
  Widget build(BuildContext context) {
    final hasText = _controller.text.isNotEmpty;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Row(
        children: [
          // 1. Expanded Search Pill (height 48, radius 24, #FAF7F5 fill, 1.5px white border)
          Expanded(
            child: Container(
              height: 48.0,
              decoration: BoxDecoration(
                color: const Color(0xFFFAF7F5),
                borderRadius: BorderRadius.circular(24.0),
                border: Border.all(color: Colors.white, width: 1.5),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x10000000),
                    blurRadius: 14.0,
                    offset: Offset(0, 5),
                  ),
                ],
              ),
              padding: const EdgeInsets.symmetric(horizontal: 14.0),
              child: Row(
                children: [
                  const Icon(
                    Icons.search_rounded,
                    size: 22.0,
                    color: Color(0xFF2C2830),
                  ),
                  const SizedBox(width: 8.0),
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      onChanged: _onTextChanged,
                      style: const TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 13.5,
                        fontWeight: FontWeight.w500,
                        color: Color(0xFF141414),
                      ),
                      decoration: const InputDecoration(
                        hintText: 'Search for a product, brand or category...',
                        hintStyle: TextStyle(
                          fontFamily: AppTypography.fontFamily,
                          fontSize: 13.5,
                          fontWeight: FontWeight.w400,
                          color: Color(0xFF78737D),
                        ),
                        border: InputBorder.none,
                        isDense: true,
                        contentPadding: EdgeInsets.zero,
                      ),
                    ),
                  ),
                  if (hasText)
                    GestureDetector(
                      onTap: _onClear,
                      child: Container(
                        padding: const EdgeInsets.all(4.0),
                        child: const Icon(
                          Icons.close_rounded,
                          size: 18.0,
                          color: Color(0xFF78737D),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 10.0),

          // 2. Standalone Barcode Shortcut Squircle (48x48, radius 15, #EAE2F3, 1.5px white border)
          Material(
            color: Colors.transparent,
            child: InkWell(
              onTap: widget.onBarcodeTap,
              borderRadius: BorderRadius.circular(15.0),
              child: Container(
                width: 48.0,
                height: 48.0,
                decoration: BoxDecoration(
                  color: const Color(0xFFEAE2F3),
                  borderRadius: BorderRadius.circular(15.0),
                  border: Border.all(color: Colors.white, width: 1.5),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x1A5A4382),
                      blurRadius: 12.0,
                      offset: Offset(0, 5),
                    ),
                  ],
                ),
                alignment: Alignment.center,
                child: const CustomPaint(
                  size: Size(22.0, 22.0),
                  painter: _BarcodeIconPainter(),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// 4 rounded black corner brackets enclosing vertical barcode bars (22x22, #1E1E1E)
class _BarcodeIconPainter extends CustomPainter {
  const _BarcodeIconPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final bracketPaint = Paint()
      ..color = const Color(0xFF1E1E1E)
      ..strokeWidth = 1.8
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    const arm = 4.5;

    // Corner brackets
    // Top-left
    canvas.drawLine(const Offset(0, arm), const Offset(0, 0), bracketPaint);
    canvas.drawLine(const Offset(0, 0), const Offset(arm, 0), bracketPaint);

    // Top-right
    canvas.drawLine(Offset(size.width - arm, 0), Offset(size.width, 0), bracketPaint);
    canvas.drawLine(Offset(size.width, 0), Offset(size.width, arm), bracketPaint);

    // Bottom-left
    canvas.drawLine(Offset(0, size.height - arm), Offset(0, size.height), bracketPaint);
    canvas.drawLine(Offset(0, size.height), Offset(arm, size.height), bracketPaint);

    // Bottom-right
    canvas.drawLine(Offset(size.width - arm, size.height), Offset(size.width, size.height), bracketPaint);
    canvas.drawLine(Offset(size.width, size.height), Offset(size.width, size.height - arm), bracketPaint);

    // Vertical barcode bars inside
    final barPaint = Paint()
      ..color = const Color(0xFF1E1E1E)
      ..style = PaintingStyle.fill;

    const barTop = 5.0;
    const barHeight = 12.0;
    final bars = [
      {'x': 5.5, 'w': 1.8},
      {'x': 9.0, 'w': 1.2},
      {'x': 12.0, 'w': 1.8},
      {'x': 15.5, 'w': 1.2},
    ];

    for (final bar in bars) {
      canvas.drawRRect(
        RRect.fromRectAndRadius(
          Rect.fromLTWH(bar['x']!, barTop, bar['w']!, barHeight),
          const Radius.circular(0.6),
        ),
        barPaint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

