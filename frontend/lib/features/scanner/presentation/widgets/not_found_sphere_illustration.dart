import 'package:flutter/material.dart';

class NotFoundSphereIllustration extends StatelessWidget {
  const NotFoundSphereIllustration({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Outer soft lavender halo circle (168x168)
          Container(
            width: 168.0,
            height: 168.0,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              gradient: RadialGradient(
                colors: [
                  Color(0xFFE8DFFA),
                  Color(0x00F2ECFA),
                ],
                stops: [0.35, 1.0],
              ),
            ),
          ),

          // Inner 3D glossy sphere (132x132)
          Container(
            width: 132.0,
            height: 132.0,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFFFFFFF),
                  Color(0xFFF3EEFF),
                  Color(0xFFD2C0FF),
                ],
                stops: [0.0, 0.45, 1.0],
              ),
              border: Border.all(color: Colors.white, width: 2.0),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x266B4CE6),
                  blurRadius: 24.0,
                  offset: Offset(0, 10),
                ),
              ],
            ),
            alignment: Alignment.center,
            // Center Not Found Icon
            child: const Icon(
              Icons.search_off_rounded,
              size: 52.0,
              color: Color(0xFF141426),
            ),
          ),
        ],
      ),
    );
  }
}

