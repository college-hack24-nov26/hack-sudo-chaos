import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../widgets/bottom_pastel_wave.dart';
import '../widgets/not_found_sphere_illustration.dart';

class ProductNotFoundScreen extends StatelessWidget {
  final String barcode;

  const ProductNotFoundScreen({
    super.key,
    required this.barcode,
  });

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

          SafeArea(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                // Top App Bar
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

                const SizedBox(height: 32.0),

                // Center 3D Glossy Sphere with Not Found icon
                const NotFoundSphereIllustration(),

                const SizedBox(height: 26.0),

                // Heading & Subtitle
                const Text(
                  'Product Not Found',
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
                  'We couldn\'t find this product in our database.\nTry scanning again or searching by name.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 14.0,
                    fontWeight: FontWeight.w400,
                    height: 1.38,
                    color: Color(0xFF565360),
                  ),
                ),

                const SizedBox(height: 24.0),

                // Scanned Barcode Details Card
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  child: Container(
                    padding: const EdgeInsets.all(16.0),
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
                      children: [
                        // Barcode Pill
                        Container(
                          height: 38.0,
                          padding: const EdgeInsets.symmetric(horizontal: 14.0),
                          decoration: BoxDecoration(
                            color: const Color(0xFFEFEAF8),
                            borderRadius: BorderRadius.circular(19.0),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              const Icon(
                                Icons.qr_code_rounded,
                                size: 18.0,
                                color: Color(0xFF5636B8),
                              ),
                              const SizedBox(width: 8.0),
                              Text(
                                barcode.isNotEmpty ? 'Barcode: $barcode' : 'Unknown Barcode',
                                style: const TextStyle(
                                  fontFamily: 'Manrope',
                                  fontSize: 13.5,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF1A1826),
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(height: 12.0),

                        // Helpful Tips
                        const _TipRow(text: 'Ensure the barcode is clearly visible and undamaged'),
                        const SizedBox(height: 6.0),
                        const _TipRow(text: 'Try typing the brand or food name in Search'),
                        const SizedBox(height: 6.0),
                        const _TipRow(text: 'Check lighting to eliminate barcode reflections'),
                      ],
                    ),
                  ),
                ),

                const Spacer(),

                // Action Buttons (Column)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0),
                  child: Column(
                    children: [
                      // Primary Button (Scan Another Barcode)
                      SizedBox(
                        width: double.infinity,
                        height: 50.0,
                        child: ElevatedButton(
                          onPressed: () {
                            if (context.canPop()) {
                              context.pop();
                            } else {
                              context.go('/scanner');
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF1E1B28),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(25.0),
                            ),
                            elevation: 0,
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.qr_code_scanner_rounded, size: 20.0, color: Colors.white),
                              SizedBox(width: 8.0),
                              Text(
                                'Scan Another Barcode',
                                style: TextStyle(
                                  fontFamily: 'Manrope',
                                  fontSize: 14.5,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 10.0),

                      // Secondary Button (Search Manually)
                      SizedBox(
                        width: double.infinity,
                        height: 50.0,
                        child: ElevatedButton(
                          onPressed: () {
                            context.push('/search');
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFF4EEFA),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(25.0),
                              side: const BorderSide(color: Colors.white, width: 1.5),
                            ),
                            elevation: 0,
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.search_rounded, size: 20.0, color: Color(0xFF1A1826)),
                              SizedBox(width: 8.0),
                              Text(
                                'Search Manually',
                                style: TextStyle(
                                  fontFamily: 'Manrope',
                                  fontSize: 14.0,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF1A1826),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24.0),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _TipRow extends StatelessWidget {
  final String text;

  const _TipRow({required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        const Icon(
          Icons.check_circle_outline_rounded,
          size: 16.0,
          color: Color(0xFF887D94),
        ),
        const SizedBox(width: 8.0),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(
              fontFamily: 'Manrope',
              fontSize: 12.0,
              fontWeight: FontWeight.w500,
              color: Color(0xFF565360),
            ),
          ),
        ),
      ],
    );
  }
}

