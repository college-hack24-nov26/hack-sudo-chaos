import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:go_router/go_router.dart';
import '../../../saved/data/models/saved_product_model.dart';
import '../../../saved/presentation/providers/saved_products_provider.dart';
import '../../../product_details/data/models/product_response_model.dart';

class IngredientTopAppBar extends ConsumerWidget {
  final ProductDetailsResponse? product;
  final VoidCallback? onBack;

  const IngredientTopAppBar({
    super.key,
    this.product,
    this.onBack,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final barcode = product?.product.barcode ?? '';
    final savedItems = ref.watch(savedProductsNotifierProvider).valueOrNull ?? [];
    final isSaved = barcode.isNotEmpty && savedItems.any((item) => item.barcode == barcode);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
      child: SizedBox(
        height: 44.0,
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Centered Logo
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

            // Right Action Squircles
            Positioned(
              right: 0,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Bookmark Squircle (42x42)
                  GestureDetector(
                    onTap: () async {
                      if (product == null) return;
                      final id = product!.product;
                      if (isSaved) {
                        await ref.read(savedProductsNotifierProvider.notifier).removeProduct(id.barcode);
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Removed from Saved Products'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        }
                      } else {
                        final savedItem = SavedProductItem(
                          barcode: id.barcode,
                          productName: id.productName,
                          category: id.foodCategory ?? 'Food',
                          brandOrQuantity: id.formattedServingSize.isNotEmpty
                              ? id.formattedServingSize
                              : (id.brandName ?? 'Standard'),
                          imageUrl: id.imageUrl,
                          savedAt: DateTime.now(),
                          badges: const [],
                        );
                        await ref.read(savedProductsNotifierProvider.notifier).saveProduct(savedItem);
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('Added to Saved Products'),
                              duration: Duration(seconds: 2),
                            ),
                          );
                        }
                      }
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
                      child: Icon(
                        isSaved ? Icons.bookmark_rounded : Icons.bookmark_border_rounded,
                        size: 20.0,
                        color: isSaved ? const Color(0xFFFF6B35) : const Color(0xFF181818),
                      ),
                    ),
                  ),

                  const SizedBox(width: 10.0),

                  // Share Squircle (42x42)
                  GestureDetector(
                    onTap: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Ingredient intelligence analysis ready to share.'),
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
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
