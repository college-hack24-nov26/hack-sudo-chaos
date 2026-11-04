import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import '../../../../app/router/app_router.dart';
import '../../../../app/theme/app_typography.dart';

class EnterBarcodeScreen extends StatefulWidget {
  const EnterBarcodeScreen({super.key});

  @override
  State<EnterBarcodeScreen> createState() => _EnterBarcodeScreenState();
}

class _EnterBarcodeScreenState extends State<EnterBarcodeScreen> {
  final TextEditingController _controller = TextEditingController();
  String? _errorMessage;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _validateAndSubmit() {
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

    FocusScope.of(context).unfocus();
    context.push('/product-loading/$barcode');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF7F5),
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: constraints.maxHeight,
                ),
                child: IntrinsicHeight(
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Top Navigation Row
                        Row(
                          children: [
                            GestureDetector(
                              onTap: () {
                                if (context.canPop()) {
                                  context.pop();
                                } else {
                                  context.go(AppRoutes.home);
                                }
                              },
                              child: Container(
                                width: 40.0,
                                height: 40.0,
                                decoration: BoxDecoration(
                                  color: Colors.white,
                                  shape: BoxShape.circle,
                                  border: Border.all(color: const Color(0xFFE5DDD5), width: 1.2),
                                  boxShadow: const [
                                    BoxShadow(
                                      color: Color(0x0A000000),
                                      blurRadius: 6.0,
                                      offset: Offset(0, 2),
                                    ),
                                  ],
                                ),
                                alignment: Alignment.center,
                                child: const Icon(
                                  Icons.arrow_back_rounded,
                                  size: 20.0,
                                  color: Color(0xFF141414),
                                ),
                              ),
                            ),
                            const Expanded(
                              child: Text(
                                'Enter Barcode',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                  fontFamily: AppTypography.fontFamily,
                                  fontSize: 16.5,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF141414),
                                  letterSpacing: -0.2,
                                ),
                              ),
                            ),
                            const SizedBox(width: 40.0), // Balance back button
                          ],
                        ),
                        const SizedBox(height: 32.0),

                        // Center Icon Badge
                        Center(
                          child: Container(
                            width: 64.0,
                            height: 64.0,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: const Color(0xFFF3EDFA),
                              border: Border.all(color: Colors.white, width: 2.0),
                              boxShadow: const [
                                BoxShadow(
                                  color: Color(0x10000000),
                                  blurRadius: 10.0,
                                  offset: Offset(0, 4),
                                ),
                              ],
                            ),
                            alignment: Alignment.center,
                            child: const Icon(
                              Icons.qr_code_rounded,
                              size: 32.0,
                              color: Color(0xFF7C5CE6),
                            ),
                          ),
                        ),
                        const SizedBox(height: 20.0),

                        // Title & Subtitle
                        const Text(
                          'Enter Barcode Manually',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontFamily: AppTypography.fontFamily,
                            fontSize: 20.0,
                            fontWeight: FontWeight.w800,
                            color: Color(0xFF141414),
                            letterSpacing: -0.3,
                          ),
                        ),
                        const SizedBox(height: 8.0),
                        const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 16.0),
                          child: Text(
                            'Type the 8, 12, or 13-digit number printed beneath the product packaging barcode.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              fontFamily: AppTypography.fontFamily,
                              fontSize: 13.0,
                              color: Color(0xFF5A5560),
                              height: 1.4,
                            ),
                          ),
                        ),
                        const SizedBox(height: 28.0),

                        // Numeric TextField
                        Container(
                          height: 54.0,
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
                                    fontSize: 16.5,
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
                        const SizedBox(height: 24.0),

                        // Submit Button
                        ElevatedButton(
                          onPressed: _validateAndSubmit,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF1D1C24),
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16.0),
                            ),
                            minimumSize: const Size(double.infinity, 52.0),
                            elevation: 0,
                          ),
                          child: const Text(
                                  'Look Up Product',
                                  style: TextStyle(
                                    fontFamily: AppTypography.fontFamily,
                                    fontSize: 14.5,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                        ),
                        const Spacer(),

                        // Bottom Help Tip Container
                        Container(
                          margin: const EdgeInsets.only(top: 24.0, bottom: 8.0),
                          padding: const EdgeInsets.all(14.0),
                          decoration: BoxDecoration(
                            color: Colors.white.withValues(alpha: 0.7),
                            borderRadius: BorderRadius.circular(16.0),
                            border: Border.all(color: const Color(0xFFEFE9F5), width: 1.2),
                          ),
                          child: const Row(
                            children: [
                              Icon(
                                Icons.lightbulb_outline_rounded,
                                size: 20.0,
                                color: Color(0xFFF47A38),
                              ),
                              SizedBox(width: 10.0),
                              Expanded(
                                child: Text(
                                  'Indian retail packaged foods usually have 13-digit EAN barcodes starting with "890".',
                                  style: TextStyle(
                                    fontFamily: AppTypography.fontFamily,
                                    fontSize: 12.0,
                                    color: Color(0xFF5A5560),
                                    height: 1.35,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}
