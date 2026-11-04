import '../../../../core/widgets/product_packet_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../saved/presentation/providers/saved_products_provider.dart';
import '../../../search/presentation/providers/search_provider.dart';
import '../../../product_details/data/models/product_response_model.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';

class ProductPickerModal extends ConsumerStatefulWidget {
  final String slotTitle;
  final ValueChanged<ProductDetailsResponse> onProductSelected;

  const ProductPickerModal({
    super.key,
    required this.slotTitle,
    required this.onProductSelected,
  });

  static Future<void> show(
    BuildContext context, {
    required String slotTitle,
    required ValueChanged<ProductDetailsResponse> onProductSelected,
  }) {
    return showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) => ProductPickerModal(
        slotTitle: slotTitle,
        onProductSelected: onProductSelected,
      ),
    );
  }

  @override
  ConsumerState<ProductPickerModal> createState() => _ProductPickerModalState();
}

class _ProductPickerModalState extends ConsumerState<ProductPickerModal>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  bool _isLoadingProduct = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _selectBarcode(String barcode) async {
    setState(() => _isLoadingProduct = true);
    try {
      final repo = ref.read(productRepositoryProvider);
      final details = await repo.getProductByBarcode(barcode);
      if (mounted) {
        Navigator.of(context).pop();
        widget.onProductSelected(details);
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoadingProduct = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to load product details: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.78,
      decoration: const BoxDecoration(
        color: Color(0xFFFDF8F4),
        borderRadius: BorderRadius.vertical(top: Radius.circular(28.0)),
        boxShadow: [
          BoxShadow(
            color: Color(0x22000000),
            blurRadius: 20.0,
            offset: Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        children: [
          // Drag handle
          Container(
            margin: const EdgeInsets.only(top: 12.0, bottom: 8.0),
            width: 40.0,
            height: 4.5,
            decoration: BoxDecoration(
              color: const Color(0xFFD4C8BC),
              borderRadius: BorderRadius.circular(3.0),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.slotTitle,
                        style: const TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 20.0,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF141414),
                        ),
                      ),
                      const SizedBox(height: 2.0),
                      const Text(
                        'Select from saved foods or search our database',
                        style: TextStyle(
                          fontFamily: 'Manrope',
                          fontSize: 12.0,
                          color: Color(0xFF6E6877),
                        ),
                      ),
                    ],
                  ),
                ),
                // Scan barcode button
                InkWell(
                  onTap: () {
                    Navigator.of(context).pop();
                    context.push('/scanner');
                  },
                  borderRadius: BorderRadius.circular(12.0),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 8.0),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFAF2EB),
                      borderRadius: BorderRadius.circular(12.0),
                      border: Border.all(color: const Color(0xFFFF6B35).withValues(alpha: 0.3)),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.qr_code_scanner_rounded, size: 16.0, color: Color(0xFFFF6B35)),
                        SizedBox(width: 4.0),
                        Text(
                          'Scan',
                          style: TextStyle(
                            fontFamily: 'Manrope',
                            fontSize: 12.0,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFFFF6B35),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 8.0),

          // Tab Bar
          TabBar(
            controller: _tabController,
            labelColor: const Color(0xFFFF6B35),
            unselectedLabelColor: const Color(0xFF7A7382),
            indicatorColor: const Color(0xFFFF6B35),
            indicatorWeight: 2.5,
            labelStyle: const TextStyle(
              fontFamily: 'Manrope',
              fontSize: 13.5,
              fontWeight: FontWeight.w700,
            ),
            tabs: const [
              Tab(text: 'Saved Foods'),
              Tab(text: 'Search Database'),
            ],
          ),

          if (_isLoadingProduct)
            const Expanded(
              child: Center(
                child: CircularProgressIndicator(color: Color(0xFFFF6B35)),
              ),
            )
          else
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildSavedTab(),
                  _buildSearchTab(),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildSavedTab() {
    final savedState = ref.watch(savedProductsNotifierProvider);

    return savedState.when(
      loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFFFF6B35))),
      error: (e, _) => Center(child: Text('Error loading saved foods: $e')),
      data: (items) {
        if (items.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.bookmark_border_rounded, size: 48.0, color: Colors.grey.shade400),
                const SizedBox(height: 12.0),
                const Text(
                  'No saved foods yet',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 15.0,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF2C2636),
                  ),
                ),
                const SizedBox(height: 4.0),
                const Text(
                  'Search or scan foods to bookmark them for easy comparison',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12.0, color: Color(0xFF7A7382)),
                ),
              ],
            ),
          );
        }

        return ListView.separated(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 14.0),
          itemCount: items.length,
          separatorBuilder: (_, __) => const SizedBox(height: 10.0),
          itemBuilder: (context, index) {
            final item = items[index];
            return InkWell(
              onTap: () => _selectBarcode(item.barcode),
              borderRadius: BorderRadius.circular(16.0),
              child: Container(
                padding: const EdgeInsets.all(12.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16.0),
                  border: Border.all(color: const Color(0xFFECE5DE)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 48.0,
                      height: 48.0,
                      child: ProductPacketImage(
                        imageUrl: item.imageUrl,
                        barcode: item.barcode,
                        category: item.category,
                        width: 48.0,
                        height: 48.0,
                        fit: BoxFit.contain,
                        borderRadius: BorderRadius.circular(10.0),
                        backgroundColor: const Color(0xFFFAF6F2),
                      ),
                    ),
                    const SizedBox(width: 12.0),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            item.productName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontFamily: 'Manrope',
                              fontSize: 14.0,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF141414),
                            ),
                          ),
                          const SizedBox(height: 2.0),
                          Text(
                            item.brandOrQuantity,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(
                              fontFamily: 'Manrope',
                              fontSize: 11.5,
                              color: Color(0xFF6E6877),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const Icon(Icons.add_circle_outline_rounded, color: Color(0xFFFF6B35)),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildSearchTab() {
    final searchAsync = ref.watch(searchResultsProvider);
    final query = ref.watch(searchQueryProvider);

    return Column(
      children: [
        // Search text input
        Padding(
          padding: const EdgeInsets.fromLTRB(20.0, 14.0, 20.0, 8.0),
          child: Container(
            height: 46.0,
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14.0),
              border: Border.all(color: const Color(0xFFE2DDD8)),
            ),
            child: TextField(
              controller: _searchController,
              onSubmitted: (val) {
                ref.read(searchQueryProvider.notifier).state = val.trim();
              },
              decoration: InputDecoration(
                hintText: 'Search food name or brand...',
                hintStyle: const TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 13.0,
                  color: Color(0xFF9E97A6),
                ),
                prefixIcon: const Icon(Icons.search_rounded, size: 20.0, color: Color(0xFF887D94)),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward_rounded, size: 20.0, color: Color(0xFFFF6B35)),
                  onPressed: () {
                    ref.read(searchQueryProvider.notifier).state = _searchController.text.trim();
                  },
                ),
                border: InputBorder.none,
                contentPadding: const EdgeInsets.symmetric(vertical: 12.0),
              ),
            ),
          ),
        ),

        Expanded(
          child: query.isEmpty
              ? const Center(
                  child: Text(
                    'Type above to search real products for comparison',
                    style: TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 12.5,
                      color: Color(0xFF7A7382),
                    ),
                  ),
                )
              : searchAsync.when(
                  loading: () => const Center(child: CircularProgressIndicator(color: Color(0xFFFF6B35))),
                  error: (err, _) => Center(child: Text('Search error: $err')),
                  data: (items) {
                    if (items.isEmpty) {
                      return const Center(child: Text('No products found matching query'));
                    }
                    return ListView.separated(
                      padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 8.0),
                      itemCount: items.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 10.0),
                      itemBuilder: (context, index) {
                        final item = items[index];
                        return InkWell(
                          onTap: () => _selectBarcode(item.barcode),
                          borderRadius: BorderRadius.circular(16.0),
                          child: Container(
                            padding: const EdgeInsets.all(12.0),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(16.0),
                              border: Border.all(color: const Color(0xFFECE5DE)),
                            ),
                            child: Row(
                              children: [
                                Container(
                                  width: 48.0,
                                  height: 48.0,
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFFAF6F2),
                                    borderRadius: BorderRadius.circular(10.0),
                                  ),
                                  alignment: Alignment.center,
                                  child: item.imageUrl != null && item.imageUrl!.isNotEmpty
                                      ? Image.network(
                                          item.imageUrl!,
                                          fit: BoxFit.contain,
                                          errorBuilder: (_, __, ___) => const Icon(Icons.fastfood, size: 24.0),
                                        )
                                      : const Icon(Icons.fastfood, size: 24.0, color: Color(0xFF887D94)),
                                ),
                                const SizedBox(width: 12.0),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        item.productName,
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                          fontFamily: 'Manrope',
                                          fontSize: 14.0,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF141414),
                                        ),
                                      ),
                                      const SizedBox(height: 2.0),
                                      Text(
                                        item.subtitleFormatted,
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                          fontFamily: 'Manrope',
                                          fontSize: 11.5,
                                          color: Color(0xFF6E6877),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                                const Icon(Icons.add_circle_outline_rounded, color: Color(0xFFFF6B35)),
                              ],
                            ),
                          ),
                        );
                      },
                    );
                  },
                ),
        ),
      ],
    );
  }
}
