import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

class AiExplanationTopAppBar extends StatelessWidget {
  final VoidCallback? onReset;
  final VoidCallback? onBack;

  const AiExplanationTopAppBar({
    super.key,
    this.onReset,
    this.onBack,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
      child: SizedBox(
        height: 44.0,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Centered YumSure Logo
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

            // Left Back Button (42x42)
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

            // Right Reset / Session Button (42x42)
            Positioned(
              right: 0,
              child: GestureDetector(
                onTap: onReset,
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
                    Icons.history_rounded,
                    size: 21.0,
                    color: Color(0xFF181818),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

