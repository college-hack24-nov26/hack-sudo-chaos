import 'package:flutter/material.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/saved_product_model.dart';

class SavedSortBottomSheet extends StatelessWidget {
  final SavedSortOrder currentOrder;
  final ValueChanged<SavedSortOrder> onOrderSelected;

  const SavedSortBottomSheet({
    super.key,
    required this.currentOrder,
    required this.onOrderSelected,
  });

  static Future<void> show(
    BuildContext context, {
    required SavedSortOrder currentOrder,
    required ValueChanged<SavedSortOrder> onOrderSelected,
  }) {
    return showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (ctx) => SavedSortBottomSheet(
        currentOrder: currentOrder,
        onOrderSelected: (order) {
          onOrderSelected(order);
          Navigator.of(ctx).pop();
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20.0, 14.0, 20.0, 28.0),
      decoration: const BoxDecoration(
        color: Color(0xFFFAF7F5),
        borderRadius: BorderRadius.vertical(top: Radius.circular(28.0)),
        border: Border(top: BorderSide(color: Colors.white, width: 1.5)),
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
        crossAxisAlignment: CrossAxisAlignment.start,
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
          const SizedBox(height: 16.0),

          // Title
          const Text(
            'Sort Saved Products',
            style: TextStyle(
              fontFamily: AppTypography.fontFamily,
              fontSize: 18.0,
              fontWeight: FontWeight.w800,
              color: Color(0xFF141414),
              letterSpacing: -0.3,
            ),
          ),
          const SizedBox(height: 14.0),

          // Option 1: Recently Saved
          _buildOption(
            title: 'Recently Saved',
            subtitle: 'Newest additions shown first',
            isSelected: currentOrder == SavedSortOrder.recentlySaved,
            onTap: () => onOrderSelected(SavedSortOrder.recentlySaved),
          ),
          const SizedBox(height: 10.0),

          // Option 2: Alphabetical (A-Z)
          _buildOption(
            title: 'Alphabetical (A–Z)',
            subtitle: 'Sort products by product name',
            isSelected: currentOrder == SavedSortOrder.alphabetical,
            onTap: () => onOrderSelected(SavedSortOrder.alphabetical),
          ),
        ],
      ),
    );
  }

  Widget _buildOption({
    required String title,
    required String subtitle,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16.0),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          decoration: BoxDecoration(
            color: isSelected ? const Color(0xFF1D1C24) : Colors.white,
            borderRadius: BorderRadius.circular(16.0),
            border: Border.all(
              color: isSelected ? const Color(0xFF1D1C24) : const Color(0xFFEBE4DC),
              width: 1.0,
            ),
            boxShadow: const [
              BoxShadow(
                color: Color(0x08000000),
                blurRadius: 8.0,
                offset: Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 14.0,
                      fontWeight: FontWeight.w700,
                      color: isSelected ? Colors.white : const Color(0xFF141414),
                    ),
                  ),
                  const SizedBox(height: 2.0),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontFamily: AppTypography.fontFamily,
                      fontSize: 12.0,
                      color: isSelected ? const Color(0xFFD6D0DC) : const Color(0xFF6E6877),
                    ),
                  ),
                ],
              ),
              if (isSelected)
                const Icon(
                  Icons.check_circle_rounded,
                  size: 20.0,
                  color: Colors.white,
                ),
            ],
          ),
        ),
      ),
    );
  }
}

