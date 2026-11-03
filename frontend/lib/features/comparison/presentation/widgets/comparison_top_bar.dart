import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

class ComparisonTopBar extends StatelessWidget {
  final VoidCallback? onBack;
  final VoidCallback? onShare;

  const ComparisonTopBar({
    super.key,
    this.onBack,
    this.onShare,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Row containing Back Button, Centered Wordmark, and Share Button
          SizedBox(
            height: 44.0,
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Centered YumSure Wordmark with smile
                Center(
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      SvgPicture.asset(
                        'assets/images/yumsure_logo.svg',
                        height: 25.0,
                        semanticsLabel: 'YumSure Logo',
                      ),
                    ],
                  ),
                ),

                // Left Back Button (42x42 squircle)
                Positioned(
                  left: 0,
                  child: GestureDetector(
                    onTap: onBack ?? () {
                      if (context.canPop()) {
                        context.pop();
                      } else {
                        context.go('/home');
                      }
                    },
                    child: Container(
                      width: 42.0,
                      height: 42.0,
                      decoration: BoxDecoration(
                        color: const Color(0xFFFAF6F2),
                        borderRadius: BorderRadius.circular(13.0),
                        border: Border.all(color: Colors.white, width: 1.2),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x10000000),
                            blurRadius: 8.0,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      alignment: Alignment.center,
                      child: const Icon(
                        Icons.arrow_back_rounded,
                        size: 21.0,
                        color: Color(0xFF181818),
                      ),
                    ),
                  ),
                ),

                // Right Share Button (42x42 lavender squircle)
                Positioned(
                  right: 0,
                  child: GestureDetector(
                    onTap: onShare ?? () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Product comparison ready to share.'),
                          duration: Duration(seconds: 2),
                        ),
                      );
                    },
                    child: Container(
                      width: 42.0,
                      height: 42.0,
                      decoration: BoxDecoration(
                        color: const Color(0xFFEDE5F6),
                        borderRadius: BorderRadius.circular(13.0),
                        border: Border.all(color: Colors.white, width: 1.2),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x185A4382),
                            blurRadius: 8.0,
                            offset: Offset(0, 2),
                          ),
                        ],
                      ),
                      alignment: Alignment.center,
                      child: const Icon(
                        Icons.ios_share_rounded,
                        size: 20.0,
                        color: Color(0xFF181818),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14.0),

          // Title & Subtitle
          const Text(
            'Compare Products',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 26.0,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.6,
              color: Color(0xFF141414),
              height: 1.2,
            ),
          ),
          const SizedBox(height: 4.0),
          const Text(
            'See the key nutritional differences and make a smarter choice.',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 12.8,
              fontWeight: FontWeight.w400,
              color: Color(0xFF5A5560),
              height: 1.35,
            ),
          ),
        ],
      ),
    );
  }
}

