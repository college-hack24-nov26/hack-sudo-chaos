import 'package:flutter/material.dart';

class IngredientFilterPills extends StatelessWidget {
  final String activeSection;
  final ValueChanged<String> onSelectSection;

  const IngredientFilterPills({
    super.key,
    required this.activeSection,
    required this.onSelectSection,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: SizedBox(
        height: 40.0,
        child: ListView(
          scrollDirection: Axis.horizontal,
          physics: const BouncingScrollPhysics(),
          children: [
            // 1. Ingredients
            _buildPill(
              sectionKey: 'ingredients',
              icon: Icons.eco_outlined,
              label: 'Ingredients',
              isSelected: activeSection == 'ingredients',
            ),

            const SizedBox(width: 8.0),

            // 2. Additives (INS)
            _buildAdditivesPill(
              isSelected: activeSection == 'additives',
            ),

            const SizedBox(width: 8.0),

            // 3. Allergens
            _buildPill(
              sectionKey: 'allergens',
              icon: Icons.shield_outlined,
              label: 'Allergens',
              isSelected: activeSection == 'allergens',
            ),

            const SizedBox(width: 8.0),

            // 4. Claims
            _buildPill(
              sectionKey: 'claims',
              icon: Icons.workspace_premium_outlined,
              label: 'Claims',
              isSelected: activeSection == 'claims',
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPill({
    required String sectionKey,
    required IconData icon,
    required String label,
    required bool isSelected,
  }) {
    return GestureDetector(
      onTap: () => onSelectSection(sectionKey),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        height: 40.0,
        padding: const EdgeInsets.symmetric(horizontal: 14.0),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF22212A) : const Color(0xFFFAF7F5),
          borderRadius: BorderRadius.circular(20.0),
          border: isSelected ? null : Border.all(color: Colors.white, width: 1.2),
          boxShadow: isSelected
              ? const [
                  BoxShadow(
                    color: Color(0x20000000),
                    blurRadius: 8.0,
                    offset: Offset(0, 3),
                  ),
                ]
              : const [
                  BoxShadow(
                    color: Color(0x0A000000),
                    blurRadius: 6.0,
                    offset: Offset(0, 2),
                  ),
                ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16.0,
              color: isSelected ? Colors.white : const Color(0xFF181818),
            ),
            const SizedBox(width: 6.0),
            Text(
              label,
              style: TextStyle(
                fontFamily: 'Manrope',
                fontSize: 12.5,
                fontWeight: FontWeight.w700,
                color: isSelected ? Colors.white : const Color(0xFF181818),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAdditivesPill({required bool isSelected}) {
    return GestureDetector(
      onTap: () => onSelectSection('additives'),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        height: 40.0,
        padding: const EdgeInsets.symmetric(horizontal: 14.0),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF22212A) : const Color(0xFFFAF7F5),
          borderRadius: BorderRadius.circular(20.0),
          border: isSelected ? null : Border.all(color: Colors.white, width: 1.2),
          boxShadow: isSelected
              ? const [
                  BoxShadow(
                    color: Color(0x20000000),
                    blurRadius: 8.0,
                    offset: Offset(0, 3),
                  ),
                ]
              : const [
                  BoxShadow(
                    color: Color(0x0A000000),
                    blurRadius: 6.0,
                    offset: Offset(0, 2),
                  ),
                ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.science_outlined,
              size: 16.0,
              color: isSelected ? Colors.white : const Color(0xFF181818),
            ),
            const SizedBox(width: 6.0),
            RichText(
              text: TextSpan(
                style: const TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 12.5,
                ),
                children: [
                  TextSpan(
                    text: 'Additives ',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: isSelected ? Colors.white : const Color(0xFF181818),
                    ),
                  ),
                  TextSpan(
                    text: '(INS)',
                    style: TextStyle(
                      fontWeight: FontWeight.w400,
                      color: isSelected ? const Color(0xFFE0D8ED) : const Color(0xFF5A5560),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

