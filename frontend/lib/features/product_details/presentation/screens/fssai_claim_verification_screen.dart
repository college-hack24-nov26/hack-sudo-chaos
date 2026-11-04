import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/widgets/product_packet_image.dart';
import '../../data/models/product_response_model.dart';
import '../providers/product_details_provider.dart';

/// Screen displaying FSSAI Claim Verification details for a product,
/// matching design_references/fssai_claim_verification.png 1:1.
class FssaiClaimVerificationScreen extends ConsumerStatefulWidget {
  final String barcode;
  final ProductDetailsResponse? initialDetails;

  const FssaiClaimVerificationScreen({
    super.key,
    required this.barcode,
    this.initialDetails,
  });

  @override
  ConsumerState<FssaiClaimVerificationScreen> createState() => _FssaiClaimVerificationScreenState();
}

class _FssaiClaimVerificationScreenState extends ConsumerState<FssaiClaimVerificationScreen> {
  int _selectedClaimIndex = 0;

  @override
  Widget build(BuildContext context) {
    if (widget.initialDetails != null) {
      return _buildContent(widget.initialDetails!);
    }

    if (widget.barcode.isEmpty) {
      return _buildContent(_demoFallbackDetails);
    }

    final productAsync = ref.watch(productDetailsFamily(widget.barcode));

    return productAsync.when(
      loading: () => const Scaffold(
        backgroundColor: Color(0xFFFAF7F5),
        body: Center(
          child: CircularProgressIndicator(
            strokeWidth: 2.5,
            color: Color(0xFFF47A38),
          ),
        ),
      ),
      error: (err, _) => _buildContent(_demoFallbackDetails),
      data: (details) => _buildContent(details),
    );
  }

  Widget _buildContent(ProductDetailsResponse details) {
    final product = details.product;
    final category = product.foodCategory?.isNotEmpty == true
        ? product.foodCategory!
        : (product.brandName?.isNotEmpty == true ? product.brandName! : 'Packaged Food');
    final quantity = product.formattedServingSize.isNotEmpty
        ? product.formattedServingSize
        : (product.packageSize?.isNotEmpty == true ? product.packageSize! : '100 g');
    final subtitleText = '$category  •  $quantity';

    final claims = details.regulatoryClaimsValidation?.claims ?? [];
    final hasClaims = claims.isNotEmpty;
    final selectedClaim = hasClaims ? claims[_selectedClaimIndex.clamp(0, claims.length - 1)] : null;

    return Scaffold(
      backgroundColor: const Color(0xFFFAF7F5),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFFFAF7F5),
              Color(0xFFF8F3FA),
              Color(0xFFF3EEFA),
            ],
            stops: [0.0, 0.45, 1.0],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // -------------------------------------------------------------
              // Section A: Top App Bar (44dp centered stack, back squircle)
              // -------------------------------------------------------------
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
                child: SizedBox(
                  height: 44.0,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      // Left Back Button (42x42 squircle)
                      Positioned(
                        left: 0,
                        child: GestureDetector(
                          onTap: () {
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
                              color: Color(0xFF161624),
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

              // -------------------------------------------------------------
              // Main Scrollable Area (Guaranteed Zero Overflow)
              // -------------------------------------------------------------
              Expanded(
                child: SingleChildScrollView(
                  physics: const BouncingScrollPhysics(),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SizedBox(height: 12.0),

                      // -------------------------------------------------------
                      // Section B: Screen Title Row with Purple Seal Badge
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            // Left Seal/Rosette Badge (52x52 circle)
                            Container(
                              width: 52.0,
                              height: 52.0,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                gradient: const LinearGradient(
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                  colors: [
                                    Color(0xFFF6F2FE),
                                    Color(0xFFE5DCFA),
                                  ],
                                ),
                                border: Border.all(color: Colors.white, width: 1.5),
                                boxShadow: const [
                                  BoxShadow(
                                    color: Color(0x166B4CE6),
                                    blurRadius: 14.0,
                                    offset: Offset(0, 6),
                                  ),
                                ],
                              ),
                              alignment: Alignment.center,
                              child: const Icon(
                                Icons.workspace_premium_outlined,
                                size: 28.0,
                                color: Color(0xFF6E52E8),
                              ),
                            ),

                            const SizedBox(width: 14.0),

                            // Heading & Subtitle
                            const Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'FSSAI Claim Verification',
                                    style: TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 21.5,
                                      fontWeight: FontWeight.w800,
                                      letterSpacing: -0.5,
                                      color: Color(0xFF121222),
                                    ),
                                  ),
                                  SizedBox(height: 4.0),
                                  Text(
                                    'Checks product claims against\nFSSAI regulations (2018).',
                                    style: TextStyle(
                                      fontFamily: 'Manrope',
                                      fontSize: 13.2,
                                      fontWeight: FontWeight.w400,
                                      height: 1.35,
                                      color: Color(0xFF4E4B59),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 16.0),

                      // -------------------------------------------------------
                      // Section C: Product Identification Card
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFAF8FA),
                            borderRadius: BorderRadius.circular(22.0),
                            border: Border.all(color: Colors.white, width: 1.5),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x08000000),
                                blurRadius: 16.0,
                                offset: Offset(0, 6),
                              ),
                            ],
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              // Left Product Thumbnail (width: 66, height: 72)
                              Container(
                                width: 66.0,
                                height: 72.0,
                                alignment: Alignment.center,
                                child: ProductPacketImage(
                                  imageUrl: product.imageUrl,
                                  barcode: product.barcode,
                                  category: product.foodCategory,
                                  width: 66.0,
                                  height: 72.0,
                                  fit: BoxFit.contain,
                                ),
                              ),

                              const SizedBox(width: 16.0),

                              // Right Details Column
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      product.productName.isNotEmpty
                                          ? product.productName
                                          : 'Packaged Food',
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                        fontFamily: 'Manrope',
                                        fontSize: 18.5,
                                        fontWeight: FontWeight.w800,
                                        letterSpacing: -0.4,
                                        color: Color(0xFF121222),
                                      ),
                                    ),
                                    const SizedBox(height: 4.0),
                                    Text(
                                      subtitleText,
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                        fontFamily: 'Manrope',
                                        fontSize: 13.5,
                                        fontWeight: FontWeight.w500,
                                        color: Color(0xFF565362),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 20.0),

                      // -------------------------------------------------------
                      // Section D: Claims on Pack — Dual Capsules
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Claims on Pack',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 18.5,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -0.4,
                                color: Color(0xFF121222),
                              ),
                            ),
                            const SizedBox(height: 10.0),

                            if (!hasClaims) ...[
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 16.0),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFFAF8FA),
                                  borderRadius: BorderRadius.circular(20.0),
                                  border: Border.all(color: Colors.white, width: 1.2),
                                ),
                                child: const Text(
                                  'No packaging claims declared on this product label',
                                  style: TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 13.5,
                                    fontWeight: FontWeight.w500,
                                    color: Color(0xFF6C6978),
                                  ),
                                ),
                              ),
                            ] else ...[
                              for (int i = 0; i < claims.length; i++) ...[
                                if (i > 0) const SizedBox(height: 10.0),
                                GestureDetector(
                                  onTap: () {
                                    setState(() => _selectedClaimIndex = i);
                                  },
                                  child: _DualPillClaimRow(
                                    claim: claims[i],
                                    isSelected: i == _selectedClaimIndex,
                                  ),
                                ),
                              ],
                            ],
                          ],
                        ),
                      ),

                      const SizedBox(height: 18.0),

                      // -------------------------------------------------------
                      // Section E: Verification Details Card with Peach Banner
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20.0),
                        child: Container(
                          decoration: BoxDecoration(
                            color: const Color(0xFFFAF8FA),
                            borderRadius: BorderRadius.circular(24.0),
                            border: Border.all(color: Colors.white, width: 1.5),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x0A000000),
                                blurRadius: 18.0,
                                offset: Offset(0, 6),
                              ),
                            ],
                          ),
                          clipBehavior: Clip.antiAlias,
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Top Full-Bleed Peach Header Strip
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 13.0),
                                decoration: const BoxDecoration(
                                  gradient: LinearGradient(
                                    begin: Alignment.centerLeft,
                                    end: Alignment.centerRight,
                                    colors: [
                                      Color(0xFFFDF1DC), // Soft peach left
                                      Color(0xFFFAE6C6), // Warmer peach right
                                    ],
                                  ),
                                ),
                                child: const Row(
                                  children: [
                                    Icon(
                                      Icons.description_outlined,
                                      size: 22.0,
                                      color: Color(0xFF6E4715),
                                    ),
                                    SizedBox(width: 10.0),
                                    Text(
                                      'Verification Details',
                                      style: TextStyle(
                                        fontFamily: 'Manrope',
                                        fontSize: 17.5,
                                        fontWeight: FontWeight.w800,
                                        color: Color(0xFF161422),
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              // Table Body
                              if (selectedClaim == null) ...[
                                const Padding(
                                  padding: EdgeInsets.all(20.0),
                                  child: Center(
                                    child: Text(
                                      'No claim verification details available for this product.',
                                      style: TextStyle(
                                        fontFamily: 'Manrope',
                                        fontSize: 13.0,
                                        color: Color(0xFF6C6978),
                                      ),
                                    ),
                                  ),
                                ),
                              ] else ...[
                                Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                                  child: Column(
                                    children: [
                                      // Row 1: Applicable Rule
                                      Padding(
                                        padding: const EdgeInsets.symmetric(vertical: 14.0),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            const SizedBox(
                                              width: 114.0,
                                              child: Text(
                                                'Applicable Rule',
                                                style: TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 13.5,
                                                  fontWeight: FontWeight.w700,
                                                  color: Color(0xFF181624),
                                                ),
                                              ),
                                            ),
                                            Expanded(
                                              child: Text(
                                                selectedClaim.applicableRule,
                                                style: const TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 13.2,
                                                  fontWeight: FontWeight.w500,
                                                  height: 1.35,
                                                  color: Color(0xFF22202E),
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),

                                      const Divider(
                                        height: 1.0,
                                        thickness: 1.0,
                                        color: Color(0xFFEFEBF2),
                                      ),

                                      // Row 2: Rule Summary
                                      Padding(
                                        padding: const EdgeInsets.symmetric(vertical: 14.0),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            const SizedBox(
                                              width: 114.0,
                                              child: Text(
                                                'Rule Summary',
                                                style: TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 13.5,
                                                  fontWeight: FontWeight.w700,
                                                  color: Color(0xFF181624),
                                                ),
                                              ),
                                            ),
                                            Expanded(
                                              child: Text(
                                                selectedClaim.resolvedRuleSummary,
                                                style: const TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 13.2,
                                                  fontWeight: FontWeight.w500,
                                                  height: 1.38,
                                                  color: Color(0xFF22202E),
                                                ),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),

                                      const Divider(
                                        height: 1.0,
                                        thickness: 1.0,
                                        color: Color(0xFFEFEBF2),
                                      ),

                                      // Row 3: Our Finding
                                      Padding(
                                        padding: const EdgeInsets.symmetric(vertical: 14.0),
                                        child: Row(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            const SizedBox(
                                              width: 114.0,
                                              child: Text(
                                                'Our Finding',
                                                style: TextStyle(
                                                  fontFamily: 'Manrope',
                                                  fontSize: 13.5,
                                                  fontWeight: FontWeight.w700,
                                                  color: Color(0xFF181624),
                                                ),
                                              ),
                                            ),
                                            Expanded(
                                              child: Column(
                                                crossAxisAlignment: CrossAxisAlignment.start,
                                                children: [
                                                  _FindingStatusBadge(
                                                    status: selectedClaim.verificationStatus,
                                                    rawStatus: selectedClaim.status,
                                                  ),
                                                  const SizedBox(height: 6.0),
                                                  Text(
                                                    selectedClaim.findingExplanation,
                                                    style: const TextStyle(
                                                      fontFamily: 'Manrope',
                                                      fontSize: 13.2,
                                                      fontWeight: FontWeight.w500,
                                                      height: 1.35,
                                                      color: Color(0xFF22202E),
                                                    ),
                                                  ),
                                                ],
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),

                      // -------------------------------------------------------
                      // Section F: Bottom Lavender Disclaimer Card
                      // -------------------------------------------------------
                      Padding(
                        padding: const EdgeInsets.fromLTRB(20.0, 16.0, 20.0, 24.0),
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 14.0),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(22.0),
                            gradient: const LinearGradient(
                              begin: Alignment.centerLeft,
                              end: Alignment.centerRight,
                              colors: [
                                Color(0xFFF4EFFD), // Lavender left
                                Color(0xFFE5D8FA), // Richer lavender right
                              ],
                            ),
                            border: Border.all(color: Colors.white, width: 1.5),
                            boxShadow: const [
                              BoxShadow(
                                color: Color(0x125A4382),
                                blurRadius: 16.0,
                                offset: Offset(0, 6),
                              ),
                            ],
                          ),
                          child: const Row(
                            children: [
                              Icon(
                                Icons.info_outline_rounded,
                                size: 23.0,
                                color: Color(0xFF262238),
                              ),
                              SizedBox(width: 12.0),
                              Expanded(
                                child: Text(
                                  'This verification is based on the declared\nclaim and available product information.\nIt is not a legal certification from FSSAI.',
                                  style: TextStyle(
                                    fontFamily: 'Manrope',
                                    fontSize: 12.8,
                                    fontWeight: FontWeight.w500,
                                    height: 1.36,
                                    color: Color(0xFF221E38),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  static const ProductDetailsResponse _demoFallbackDetails = ProductDetailsResponse(
    product: ProductIdentity(
      barcode: '8901491101837',
      productName: "Lay's Classic",
      brandName: "Lay's",
      foodCategory: 'Potato Chips',
      packageSize: '100 g',
      foodForm: 'solid',
    ),
    regulatoryClaimsValidation: RegulatoryClaimsValidation(
      applicableRegulation: 'FSSAI (Advertising and Claims) Regulations, 2018',
      isFssaiCompliant: true,
      claims: [
        RegulatoryClaimItem(
          claimCode: 'NO_ADDED_MSG',
          claimName: 'No Added MSG',
          status: 'COMPLIANT',
          regulatoryReference: 'FSSAI Advertising &\nClaims Regulations, 2018',
          explanation: 'The claim is acceptable as per the regulation.',
          ruleSummary: 'The product must not contain any added Monosodium Glutamate or glutamate flavour enhancers.',
        ),
      ],
    ),
  );
}

class _DualPillClaimRow extends StatelessWidget {
  final RegulatoryClaimItem claim;
  final bool isSelected;

  const _DualPillClaimRow({
    required this.claim,
    this.isSelected = true,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        // Left Claim Text Pill (flex: 11)
        Expanded(
          flex: 11,
          child: Container(
            constraints: const BoxConstraints(minHeight: 48.0),
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(24.0),
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFF3EEFD),
                  Color(0xFFE6DCFA),
                ],
              ),
              border: Border.all(
                color: isSelected ? const Color(0xFF6E52E8) : Colors.white,
                width: isSelected ? 1.8 : 1.5,
              ),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x0D5A4382),
                  blurRadius: 8.0,
                  offset: Offset(0, 3),
                ),
              ],
            ),
            alignment: Alignment.center,
            child: Text(
              '"${claim.claimText}"',
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontFamily: 'Manrope',
                fontSize: 14.5,
                fontWeight: FontWeight.w800,
                color: Color(0xFF181528),
              ),
            ),
          ),
        ),

        const SizedBox(width: 12.0),

        // Right Verification Status Pill (flex: 9)
        Expanded(
          flex: 9,
          child: _StatusCapsulePill(
            status: claim.verificationStatus,
            rawStatus: claim.status,
          ),
        ),
      ],
    );
  }
}

class _StatusCapsulePill extends StatelessWidget {
  final ClaimVerificationStatus status;
  final String rawStatus;

  const _StatusCapsulePill({
    required this.status,
    required this.rawStatus,
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Gradient? gradient;
    Color border = Colors.white;
    Color fg;
    IconData icon;
    String label;

    switch (status) {
      case ClaimVerificationStatus.compliant:
        bg = const Color(0xFFE3F6EA);
        gradient = const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFE3F6EA),
            Color(0xFFD4F2DF),
          ],
        );
        fg = const Color(0xFF1B6E32);
        icon = Icons.check_circle_outline_rounded;
        label = 'Compliant';
        break;
      case ClaimVerificationStatus.nonCompliant:
        bg = const Color(0xFFFDE8E8);
        fg = const Color(0xFFA61E1E);
        icon = Icons.highlight_off_rounded;
        label = 'Non-compliant';
        break;
      case ClaimVerificationStatus.insufficientInformation:
        bg = const Color(0xFFFDF0DC);
        fg = const Color(0xFF8A4F0D);
        icon = Icons.help_outline_rounded;
        label = 'Insufficient Info';
        break;
      case ClaimVerificationStatus.unableToVerify:
        bg = const Color(0xFFFDF0DC);
        fg = const Color(0xFF8A4F0D);
        icon = Icons.help_outline_rounded;
        label = 'Unable to verify';
        break;
    }

    return Container(
      constraints: const BoxConstraints(minHeight: 48.0),
      padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
      decoration: BoxDecoration(
        color: gradient == null ? bg : null,
        gradient: gradient,
        borderRadius: BorderRadius.circular(24.0),
        border: Border.all(color: border, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0A000000),
            blurRadius: 8.0,
            offset: Offset(0, 3),
          ),
        ],
      ),
      alignment: Alignment.center,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 18.0, color: fg),
          const SizedBox(width: 6.0),
          Flexible(
            child: Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontFamily: 'Manrope',
                fontSize: 14.0,
                fontWeight: FontWeight.w700,
                color: fg,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _FindingStatusBadge extends StatelessWidget {
  final ClaimVerificationStatus status;
  final String rawStatus;

  const _FindingStatusBadge({
    required this.status,
    required this.rawStatus,
  });

  @override
  Widget build(BuildContext context) {
    Color bg;
    Color fg;
    IconData icon;
    String label;

    switch (status) {
      case ClaimVerificationStatus.compliant:
        bg = const Color(0xFFE3F6EA);
        fg = const Color(0xFF1B6E32);
        icon = Icons.check_circle_outline_rounded;
        label = 'Compliant';
        break;
      case ClaimVerificationStatus.nonCompliant:
        bg = const Color(0xFFFDE8E8);
        fg = const Color(0xFFA61E1E);
        icon = Icons.highlight_off_rounded;
        label = 'Non-compliant';
        break;
      case ClaimVerificationStatus.insufficientInformation:
        bg = const Color(0xFFFDF0DC);
        fg = const Color(0xFF8A4F0D);
        icon = Icons.help_outline_rounded;
        label = 'Insufficient Info';
        break;
      case ClaimVerificationStatus.unableToVerify:
        bg = const Color(0xFFFDF0DC);
        fg = const Color(0xFF8A4F0D);
        icon = Icons.help_outline_rounded;
        label = 'Unable to verify';
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 4.0),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(12.0),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14.0, color: fg),
          const SizedBox(width: 4.0),
          Text(
            label,
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 12.5,
              fontWeight: FontWeight.w700,
              color: fg,
            ),
          ),
        ],
      ),
    );
  }
}
