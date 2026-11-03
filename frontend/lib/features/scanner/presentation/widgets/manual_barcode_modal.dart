import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../app/theme/app_typography.dart';

class ManualBarcodeModal extends StatefulWidget {
  final Future<void> Function(String barcode) onSubmit;

  const ManualBarcodeModal({super.key, required this.onSubmit});

  static Future<void> show(
    BuildContext context, {
    required Future<void> Function(String barcode) onSubmit,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => ManualBarcodeModal(onSubmit: onSubmit),
    );
  }

  @override
  State<ManualBarcodeModal> createState() => _ManualBarcodeModalState();
}

class _ManualBarcodeModalState extends State<ManualBarcodeModal> {
  final TextEditingController _controller = TextEditingController();
  String? _errorMessage;
  bool _isLoading = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _validateAndSubmit() async {
    final barcode = _controller.text.trim();
    if (barcode.isEmpty) {
      setState(() => _errorMessage = 'Please enter a barcode number');
      return;
    }
    if (!RegExp(r'^\d+$').hasMatch(barcode)) {
      setState(() => _errorMessage = 'Barcode must contain digits only');
      return;
    }
    if (barcode.length < 6 || barcode.length > 14) {
      setState(() => _errorMessage = 'Barcode must be between 6 and 14 digits (e.g. EAN-13, EAN-8, UPC)');
      return;
    }

    setState(() {
      _errorMessage = null;
      _isLoading = true;
    });

    try {
      await widget.onSubmit(barcode);
      if (mounted) {
        Navigator.of(context).pop();
      }
    } catch (_) {
      // Errors handled by caller
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final bottomInset = MediaQuery.of(context).viewInsets.bottom;

    return Container(
      padding: EdgeInsets.fromLTRB(24.0, 16.0, 24.0, 24.0 + bottomInset),
      decoration: const BoxDecoration(
        color: Color(0xFFFAF7F5),
        borderRadius: BorderRadius.vertical(top: Radius.circular(30.0)),
        border: Border(
          top: BorderSide(color: Colors.white, width: 1.5),
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
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40.0,
              height: 4.5,
              decoration: BoxDecoration(
                color: const Color(0xFFC4BDCB),
                borderRadius: BorderRadius.circular(3.0),
              ),
            ),
          ),
          const SizedBox(height: 18.0),

          // Title & Subtitle
          const Text(
            'Enter Barcode Manually',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 18.0,
              fontWeight: FontWeight.w800,
              color: Color(0xFF141414),
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 6.0),
          const Text(
            'Type the 8, 12, or 13-digit number printed beneath the product packaging barcode.',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 12.5,
              color: Color(0xFF5A5560),
              height: 1.35,
            ),
          ),
          const SizedBox(height: 20.0),

          // Numeric TextField
          Container(
            height: 52.0,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16.0),
              border: Border.all(
                color: _errorMessage != null ? Colors.redAccent : const Color(0xFFE5DDD5),
                width: 1.2,
              ),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x08000000),
                  blurRadius: 8.0,
                  offset: Offset(0, 3),
                ),
              ],
            ),
            padding: const EdgeInsets.symmetric(horizontal: 14.0),
            child: Row(
              children: [
                const Icon(
                  Icons.qr_code_rounded,
                  size: 22.0,
                  color: Color(0xFF6E6877),
                ),
                const SizedBox(width: 10.0),
                Expanded(
                  child: TextField(
                    controller: _controller,
                    autofocus: true,
                    keyboardType: TextInputType.number,
                    inputFormatters: [
                      FilteringTextInputFormatter.digitsOnly,
                      LengthLimitingTextInputFormatter(14),
                    ],
                    onChanged: (_) {
                      if (_errorMessage != null) {
                        setState(() => _errorMessage = null);
                      }
                    },
                    onSubmitted: (_) => _validateAndSubmit(),
                    style: const TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 16.0,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.5,
                      color: Color(0xFF141414),
                    ),
                    decoration: const InputDecoration(
                      hintText: 'e.g. 8901030383701',
                      hintStyle: TextStyle(
                        fontFamily: AppTypography.fontFamily,
                        fontSize: 14.0,
                        fontWeight: FontWeight.w400,
                        letterSpacing: 0.5,
                        color: Color(0xFF9E98A5),
                      ),
                      border: InputBorder.none,
                      isDense: true,
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ),
                if (_controller.text.isNotEmpty)
                  GestureDetector(
                    onTap: () {
                      _controller.clear();
                      setState(() => _errorMessage = null);
                    },
                    child: const Icon(
                      Icons.cancel_rounded,
                      size: 18.0,
                      color: Color(0xFF9E98A5),
                    ),
                  ),
              ],
            ),
          ),
          if (_errorMessage != null) ...[
            const SizedBox(height: 6.0),
            Padding(
              padding: const EdgeInsets.only(left: 4.0),
              child: Text(
                _errorMessage!,
                style: const TextStyle(
                  fontFamily: AppTypography.fontFamily,
                  fontSize: 11.5,
                  fontWeight: FontWeight.w600,
                  color: Colors.redAccent,
                ),
              ),
            ),
          ],
          const SizedBox(height: 20.0),

          // Submit Button
          ElevatedButton(
            onPressed: _isLoading ? null : _validateAndSubmit,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1D1C24),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16.0),
              ),
              minimumSize: const Size(double.infinity, 50.0),
              elevation: 0,
            ),
            child: _isLoading
                ? const SizedBox(
                    width: 20.0,
                    height: 20.0,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.0,
                      color: Colors.white,
                    ),
                  )
                : const Text(
                    'Look Up Product',
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 14.5,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
          ),
        ],
      ),
    );
  }
}
