import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/network/api_exceptions.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../widgets/bottom_pastel_wave.dart';
import '../widgets/loading_scanner_sphere.dart';
import '../widgets/loading_stage_progress_card.dart';

class ProductLoadingScreen extends ConsumerStatefulWidget {
  final String barcode;

  const ProductLoadingScreen({
    super.key,
    required this.barcode,
  });

  @override
  ConsumerState<ProductLoadingScreen> createState() => _ProductLoadingScreenState();
}

class _ProductLoadingScreenState extends ConsumerState<ProductLoadingScreen> {
  LoadingStage _stage = LoadingStage.fetchingData;
  String? _errorMessage;
  bool _isCancelled = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startProductLookup();
    });
  }

  @override
  void dispose() {
    _isCancelled = true;
    super.dispose();
  }

  Future<void> _startProductLookup() async {
    final barcode = widget.barcode.trim();
    if (barcode.isEmpty) {
      if (mounted) context.go('/home');
      return;
    }

    setState(() {
      _stage = LoadingStage.fetchingData;
      _errorMessage = null;
    });

    try {
      final repo = ref.read(productRepositoryProvider);
      final productDetails = await repo.getProductByBarcode(barcode);

      if (_isCancelled || !mounted) return;

      setState(() => _stage = LoadingStage.processingNutrition);
      await Future.delayed(const Duration(milliseconds: 250));

      if (_isCancelled || !mounted) return;

      setState(() => _stage = LoadingStage.preparingInsights);
      await Future.delayed(const Duration(milliseconds: 200));

      if (_isCancelled || !mounted) return;

      setState(() => _stage = LoadingStage.completed);

      // Navigate to product details screen
      if (productDetails.hasIncompleteData) {
        context.replace('/product/$barcode/incomplete-data');
      } else {
        context.replace('/product/$barcode');
      }
    } on ProductNotFoundException {
      if (_isCancelled || !mounted) return;
      context.replace('/product-not-found/$barcode');
    } catch (e) {
      if (_isCancelled || !mounted) return;
      setState(() {
        _errorMessage = e is ApiException ? e.message : e.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF6F4),
      body: Stack(
        children: [
          // Background soft gradient
          Positioned.fill(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFFFAF6F4),
                    Color(0xFFF7F2FB),
                    Color(0xFFF2ECFA),
                  ],
                ),
              ),
            ),
          ),

          // Bottom Flowing Pastel Wave Decoration
          const Positioned(
            left: 0,
            right: 0,
            bottom: 0,
            child: BottomPastelWave(),
          ),

          // Main Content Area
          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Section 1: Top App Bar
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
                  child: SizedBox(
                    height: 44.0,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        // Left Back Button (42x42)
                        Positioned(
                          left: 0,
                          child: GestureDetector(
                            onTap: () {
                              _isCancelled = true;
                              if (context.canPop()) {
                                context.pop();
                              } else {
                                context.go('/scanner');
                              }
                            },
                            child: Container(
                              width: 42.0,
                              height: 42.0,
                              decoration: BoxDecoration(
                                color: const Color(0xFFFAF7F5),
                                borderRadius: BorderRadius.circular(14.0),
                                border: Border.all(color: Colors.white, width: 1.2),
                                boxShadow: const [
                                  BoxShadow(
                                    color: Color(0x0F000000),
                                    blurRadius: 8.0,
                                    offset: Offset(0, 2),
                                  ),
                                ],
                              ),
                              alignment: Alignment.center,
                              child: const Icon(
                                Icons.arrow_back_rounded,
                                size: 20.0,
                                color: Color(0xFF161622),
                              ),
                            ),
                          ),
                        ),

                        // Center YumSure Wordmark with smile
                        Center(
                          child: SvgPicture.asset(
                            'assets/images/yumsure_logo.svg',
                            height: 24.0,
                            semanticsLabel: 'YumSure Logo',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 36.0),

                // Section 2: Center 3D Glossy Scanner Sphere
                const LoadingScannerSphere(),

                const SizedBox(height: 28.0),

                // Section 3: Heading & Subtitle
                const Text(
                  'Analyzing Product...',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 24.0,
                    fontWeight: FontWeight.w800,
                    letterSpacing: -0.5,
                    color: Color(0xFF121222),
                  ),
                ),
                const SizedBox(height: 8.0),
                const Text(
                  'Fetching product details\nand nutrition information.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 14.0,
                    fontWeight: FontWeight.w400,
                    height: 1.38,
                    color: Color(0xFF565360),
                  ),
                ),

                const SizedBox(height: 28.0),

                // Section 4: 4-Stage Progress Card or Error Banner
                if (_errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 24.0),
                    child: Container(
                      padding: const EdgeInsets.all(16.0),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFAF8FA),
                        borderRadius: BorderRadius.circular(24.0),
                        border: Border.all(color: Colors.white, width: 1.5),
                      ),
                      child: Column(
                        children: [
                          const Icon(Icons.wifi_off_rounded, size: 36.0, color: Color(0xFFD97E26)),
                          const SizedBox(height: 8.0),
                          const Text(
                            'Network Connection Issue',
                            style: TextStyle(
                              fontFamily: 'Manrope',
                              fontSize: 15.0,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF121222),
                            ),
                          ),
                          const SizedBox(height: 4.0),
                          Text(
                            _errorMessage!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(fontSize: 12.0, color: Color(0xFF565360)),
                          ),
                          const SizedBox(height: 14.0),
                          ElevatedButton(
                            onPressed: _startProductLookup,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF6E44FF),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16.0)),
                            ),
                            child: const Text('Try Again', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                          ),
                        ],
                      ),
                    ),
                  )
                else
                  LoadingStageProgressCard(
                    currentStage: _stage,
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

