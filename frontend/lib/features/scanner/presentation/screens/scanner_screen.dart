import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../../../../app/router/app_router.dart';
import '../../../../core/network/api_exceptions.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../widgets/barcode_lookup_feedback_dialog.dart';
import '../widgets/manual_barcode_modal.dart';
import '../widgets/scanner_bottom_sheet_panel.dart';
import '../widgets/scanner_feature_highlights.dart';
import '../widgets/scanner_reticle_view.dart';
import '../widgets/scanner_top_app_bar.dart';

class ScannerScreen extends ConsumerStatefulWidget {
  const ScannerScreen({super.key});

  @override
  ConsumerState<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends ConsumerState<ScannerScreen> with WidgetsBindingObserver {
  late final MobileScannerController _scannerController;
  bool _isProcessing = false;
  bool _isTorchOn = false;
  bool _cameraPermissionError = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _scannerController = MobileScannerController(
      formats: const [
        BarcodeFormat.ean13,
        BarcodeFormat.ean8,
        BarcodeFormat.upcA,
        BarcodeFormat.upcE,
      ],
      detectionSpeed: DetectionSpeed.noDuplicates,
    );
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (!_scannerController.value.isInitialized) return;
    if (state == AppLifecycleState.inactive || state == AppLifecycleState.paused) {
      _scannerController.stop();
    } else if (state == AppLifecycleState.resumed) {
      _scannerController.start();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _scannerController.dispose();
    super.dispose();
  }

  Future<void> _toggleTorch() async {
    try {
      await _scannerController.toggleTorch();
      setState(() {
        _isTorchOn = !_isTorchOn;
      });
    } catch (_) {
      // Ignored if device has no torch
    }
  }

  Future<void> _switchCamera() async {
    try {
      await _scannerController.switchCamera();
    } catch (_) {
      // Ignored if single camera
    }
  }

  Future<void> _handleBarcodeDetection(String rawBarcode) async {
    if (_isProcessing) return;
    final barcode = rawBarcode.trim();
    if (barcode.isEmpty) return;

    _isProcessing = true;
    _lookupProduct(barcode);
  }

  Future<void> _lookupProduct(String barcode) async {
    // Validate barcode format: digits only, 6 to 14 characters
    if (!RegExp(r'^\d+$').hasMatch(barcode) || barcode.length < 6 || barcode.length > 14) {
      if (mounted) {
        BarcodeLookupFeedbackSheet.show(
          context,
          barcode: barcode,
          feedbackType: ScannerFeedbackType.invalid,
          onScanAgain: () {
            _isProcessing = false;
          },
        );
      }
      return;
    }

    // Show lightweight transparent progress overlay
    showDialog(
      context: context,
      barrierDismissible: false,
      barrierColor: Colors.black38,
      builder: (ctx) => Center(
        child: Container(
          padding: const EdgeInsets.all(24.0),
          decoration: BoxDecoration(
            color: const Color(0xFF1D1C24).withValues(alpha: 0.92),
            borderRadius: BorderRadius.circular(20.0),
            border: Border.all(color: Colors.white24, width: 1.2),
          ),
          child: const Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              CircularProgressIndicator(strokeWidth: 2.5, color: Color(0xFFF47A38)),
              SizedBox(height: 16.0),
              Text(
                'Analyzing Product...',
                style: TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 14.0,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );

    try {
      final repo = ref.read(productRepositoryProvider);
      await repo.getProductByBarcode(barcode);

      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop(); // dismiss loading dialog
        await context.push('/product/$barcode');
        _isProcessing = false;
      }
    } on ProductNotFoundException {
      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop(); // dismiss loading dialog
        BarcodeLookupFeedbackSheet.show(
          context,
          barcode: barcode,
          feedbackType: ScannerFeedbackType.notFound,
          onScanAgain: () {
            _isProcessing = false;
          },
          onEnterManually: () {
            _isProcessing = false;
            _openManualBarcodeModal();
          },
        );
      }
    } on NetworkException {
      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop(); // dismiss loading dialog
        BarcodeLookupFeedbackSheet.show(
          context,
          barcode: barcode,
          feedbackType: ScannerFeedbackType.offline,
          onScanAgain: () {
            _isProcessing = false;
          },
          onRetry: () {
            _isProcessing = false;
            _lookupProduct(barcode);
          },
        );
      }
    } on ServerException {
      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop(); // dismiss loading dialog
        BarcodeLookupFeedbackSheet.show(
          context,
          barcode: barcode,
          feedbackType: ScannerFeedbackType.offline,
          onScanAgain: () {
            _isProcessing = false;
          },
          onRetry: () {
            _isProcessing = false;
            _lookupProduct(barcode);
          },
        );
      }
    } catch (_) {
      if (mounted) {
        Navigator.of(context, rootNavigator: true).pop(); // dismiss loading dialog
        BarcodeLookupFeedbackSheet.show(
          context,
          barcode: barcode,
          feedbackType: ScannerFeedbackType.notFound,
          onScanAgain: () {
            _isProcessing = false;
          },
          onEnterManually: () {
            _isProcessing = false;
            _openManualBarcodeModal();
          },
        );
      }
    }
  }

  void _openManualBarcodeModal() {
    ManualBarcodeModal.show(
      context,
      onSubmit: (barcode) async {
        await _lookupProduct(barcode);
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final reticleWidth = screenWidth * 0.74;
    const reticleHeight = 235.0;

    return Scaffold(
      backgroundColor: const Color(0xFF2B1810),
      body: Stack(
        children: [
          // -----------------------------------------------------------
          // Layer 1: Rich Warm Ambient Camera Background
          // -----------------------------------------------------------
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Color(0xFF2B1810), // Warm dark espresso top
                    Color(0xFF21130D),
                    Color(0xFF180D09),
                  ],
                  stops: [0.0, 0.45, 1.0],
                ),
              ),
            ),
          ),

          // Warm Roasted Amber Glow behind reticle (#6E3B22)
          Positioned(
            top: 110.0,
            left: 0,
            right: 0,
            height: 340.0,
            child: IgnorePointer(
              child: Container(
                decoration: const BoxDecoration(
                  gradient: RadialGradient(
                    colors: [
                      Color(0x996E3B22),
                      Color(0x4D6E3B22),
                      Colors.transparent,
                    ],
                    stops: [0.0, 0.55, 1.0],
                  ),
                ),
              ),
            ),
          ),

          // Lower-Left Warm Golden-Peach Glow (#D48A54 at 0.55 opacity)
          Positioned(
            left: -60.0,
            bottom: 120.0,
            width: 270.0,
            height: 270.0,
            child: IgnorePointer(
              child: Container(
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Color(0x8CD48A54),
                      Color(0x3CD48A54),
                      Colors.transparent,
                    ],
                    stops: [0.0, 0.50, 1.0],
                  ),
                ),
              ),
            ),
          ),

          // Lower-Right Soft Violet-Lavender Glow (#8E74CC at 0.50 opacity)
          Positioned(
            right: -60.0,
            bottom: 120.0,
            width: 270.0,
            height: 270.0,
            child: IgnorePointer(
              child: Container(
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: RadialGradient(
                    colors: [
                      Color(0x808E74CC),
                      Color(0x308E74CC),
                      Colors.transparent,
                    ],
                    stops: [0.0, 0.50, 1.0],
                  ),
                ),
              ),
            ),
          ),

          // -----------------------------------------------------------
          // Layer 2: MobileScanner Camera Feed
          // -----------------------------------------------------------
          if (!_cameraPermissionError)
            Positioned.fill(
              child: Opacity(
                opacity: 0.90,
                child: MobileScanner(
                  controller: _scannerController,
                  onDetect: (BarcodeCapture capture) {
                    for (final barcode in capture.barcodes) {
                      if (barcode.rawValue != null) {
                        _handleBarcodeDetection(barcode.rawValue!);
                        break;
                      }
                    }
                  },
                  errorBuilder: (context, error, child) {
                    WidgetsBinding.instance.addPostFrameCallback((_) {
                      if (!_cameraPermissionError && mounted) {
                        setState(() => _cameraPermissionError = true);
                      }
                    });
                    return const SizedBox.shrink();
                  },
                ),
              ),
            ),

          // Top Vignette Overlay
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            height: MediaQuery.of(context).size.height * 0.20,
            child: IgnorePointer(
              child: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      Color(0x991A120E),
                      Color(0x001A120E),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // -----------------------------------------------------------
          // Layer 3: Main Foreground UI Structure (Exact Spacing & Zero Overflow)
          // -----------------------------------------------------------
          SafeArea(
            bottom: false,
            child: Column(
              children: [
                // Top App Bar with Centered Logo in Stack
                ScannerTopAppBar(
                  onBack: () {
                    if (context.canPop()) {
                      context.pop();
                    } else {
                      context.go(AppRoutes.home);
                    }
                  },
                  onToggleFlash: _toggleTorch,
                  onSwitchCamera: _switchCamera,
                  isFlashActive: _isTorchOn,
                ),

                // 28px gap to reticle
                const SizedBox(height: 28.0),

                // Center Barcode Reticle & Full-Width 52% Laser Line
                ScannerReticleView(
                  width: reticleWidth,
                  height: reticleHeight,
                ),

                // 22px gap to heading
                const SizedBox(height: 22.0),

                // Instruction Heading & 3 Feature Badges
                const ScannerFeatureHighlights(),

                // Remaining flexible gap to bottom sheet
                const Spacer(),

                // Docked Bottom Sheet Panel ("Other Options") - 100% visible
                ScannerBottomSheetPanel(
                  onManualBarcodeTap: _openManualBarcodeModal,
                  onSearchTap: () => context.push(AppRoutes.search),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
