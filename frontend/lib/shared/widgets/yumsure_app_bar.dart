import 'package:flutter/material.dart';
import '../../app/theme/app_colors.dart';
import '../../app/theme/app_spacing.dart';

class YumSureAppBar extends StatelessWidget implements PreferredSizeWidget {
  final VoidCallback? onBack;
  final VoidCallback? onBookmark;
  final VoidCallback? onMore;
  final bool showActions;

  const YumSureAppBar({
    super.key,
    this.onBack,
    this.onBookmark,
    this.onMore,
    this.showActions = true,
  });

  @override
  Size get preferredSize => const Size.fromHeight(60.0);

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Container(
        height: 60.0,
        padding: const EdgeInsets.symmetric(horizontal: 16.0),
        child: Row(
          children: [
            // Back Button
            _CircularIconButton(
              icon: Icons.arrow_back,
              onPressed: onBack ?? () => Navigator.maybePop(context),
            ),
            const Spacer(),
            // Stylized YumSure Brand
            const _BrandTitle(),
            const Spacer(),
            if (showActions) ...[
              _CircularIconButton(
                icon: Icons.bookmark_border_rounded,
                onPressed: onBookmark,
              ),
              const SizedBox(width: AppSpacing.sm),
              _CircularIconButton(
                icon: Icons.more_horiz_rounded,
                onPressed: onMore,
              ),
            ] else ...[
              const SizedBox(width: 40.0),
            ],
          ],
        ),
      ),
    );
  }
}

class _CircularIconButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback? onPressed;

  const _CircularIconButton({
    required this.icon,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      shape: const CircleBorder(
        side: BorderSide(color: AppColors.border, width: 1.0),
      ),
      elevation: 0,
      child: InkWell(
        onTap: onPressed,
        customBorder: const CircleBorder(),
        child: SizedBox(
          width: 40.0,
          height: 40.0,
          child: Icon(
            icon,
            size: AppSpacing.iconMd,
            color: AppColors.textPrimary,
          ),
        ),
      ),
    );
  }
}

class _BrandTitle extends StatelessWidget {
  const _BrandTitle();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        RichText(
          text: const TextSpan(
            style: TextStyle(
              fontSize: 22.0,
              fontWeight: FontWeight.w800,
              color: AppColors.textPrimary,
              letterSpacing: -0.5,
              fontFamily: 'sans-serif',
            ),
            children: [
              TextSpan(text: 'Yum'),
              TextSpan(
                text: 'Sure',
                style: TextStyle(color: AppColors.textPrimary),
              ),
            ],
          ),
        ),
        // Orange subtle curve under the brand name
        Container(
          width: 28.0,
          height: 3.0,
          margin: const EdgeInsets.only(top: 1.0),
          decoration: BoxDecoration(
            color: AppColors.brandOrange,
            borderRadius: BorderRadius.circular(2.0),
          ),
        ),
      ],
    );
  }
}
