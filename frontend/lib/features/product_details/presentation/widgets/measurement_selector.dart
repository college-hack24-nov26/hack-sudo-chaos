import 'package:flutter/material.dart';
import '../../../../app/theme/app_colors.dart';
import '../../../../app/theme/app_spacing.dart';
import '../../../../app/theme/app_typography.dart';
import '../../data/models/product_response_model.dart';

class MeasurementSelector extends StatelessWidget {
  final ProductIdentity product;
  final bool isPerServing;
  final ValueChanged<bool> onSelectionChanged;

  const MeasurementSelector({
    super.key,
    required this.product,
    required this.isPerServing,
    required this.onSelectionChanged,
  });

  @override
  Widget build(BuildContext context) {
    final hasServing = product.hasServingInfo;
    final unit100 = product.foodForm == 'liquid' ? '100 ml' : '100 g';
    final servingLabel = hasServing
        ? 'Per serving (${product.formattedServingSize})'
        : 'Per serving (N/A)';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          height: 48.0,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(AppSpacing.radiusPill),
            border: Border.all(color: AppColors.border, width: 1.0),
          ),
          padding: const EdgeInsets.all(4.0),
          child: Row(
            children: [
              // Per 100 g/ml Button
              Expanded(
                child: _SelectorButton(
                  label: 'Per $unit100',
                  isSelected: !isPerServing,
                  onTap: () => onSelectionChanged(false),
                ),
              ),
              const SizedBox(width: 4.0),
              // Per Serving Button
              Expanded(
                child: _SelectorButton(
                  label: servingLabel,
                  isSelected: isPerServing,
                  isEnabled: hasServing,
                  onTap: hasServing ? () => onSelectionChanged(true) : null,
                ),
              ),
            ],
          ),
        ),
        if (!hasServing) ...[
          const SizedBox(height: 4.0),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 12.0),
            child: Text(
              'Serving size was not declared by the manufacturer on this packaging.',
              style: TextStyle(
                fontSize: 11.0,
                color: AppColors.textTertiary,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        ],
      ],
    );
  }
}

class _SelectorButton extends StatelessWidget {
  final String label;
  final bool isSelected;
  final bool isEnabled;
  final VoidCallback? onTap;

  const _SelectorButton({
    required this.label,
    required this.isSelected,
    this.isEnabled = true,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveColor = isSelected
        ? AppColors.accentDark
        : Colors.transparent;

    final textColor = !isEnabled
        ? AppColors.textTertiary
        : isSelected
            ? Colors.white
            : AppColors.textPrimary;

    return Material(
      color: effectiveColor,
      borderRadius: BorderRadius.circular(AppSpacing.radiusPill),
      child: InkWell(
        onTap: isEnabled ? onTap : null,
        borderRadius: BorderRadius.circular(AppSpacing.radiusPill),
        child: Container(
          alignment: Alignment.center,
          padding: const EdgeInsets.symmetric(horizontal: 8.0),
          child: Text(
            label,
            style: AppTypography.label.copyWith(
              color: textColor,
              fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
    );
  }
}

