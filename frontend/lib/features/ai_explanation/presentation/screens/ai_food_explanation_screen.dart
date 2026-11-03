import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../providers/ai_explanation_provider.dart';
import '../widgets/ai_bottom_input_bar.dart';
import '../widgets/ai_conversation_thread.dart';
import '../widgets/ai_explanation_header.dart';
import '../widgets/ai_explanation_top_app_bar.dart';
import '../widgets/ai_selected_product_card.dart';
import '../widgets/ai_try_asking_grid.dart';

class AiFoodExplanationScreen extends ConsumerStatefulWidget {
  final String barcode;

  const AiFoodExplanationScreen({
    super.key,
    required this.barcode,
  });

  @override
  ConsumerState<AiFoodExplanationScreen> createState() => _AiFoodExplanationScreenState();
}

class _AiFoodExplanationScreenState extends ConsumerState<AiFoodExplanationScreen> {
  final ScrollController _scrollController = ScrollController();
  bool _hasInitializedFirstQuestion = false;

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final productAsync = ref.watch(productDetailsFamily(widget.barcode));
    final chatMessages = ref.watch(aiChatMessagesProvider);

    return Scaffold(
      backgroundColor: const Color(0xFFFDF8F4), // Base warm ivory
      body: Stack(
        children: [
          // Background Lavender Wave
          const Positioned.fill(
            child: CustomPaint(
              painter: _AiLavenderWavePainter(),
            ),
          ),

          SafeArea(
            child: Column(
              children: [
                // Section B: Top App Bar
                AiExplanationTopAppBar(
                  onReset: () {
                    ref.read(aiChatMessagesProvider.notifier).resetSession();
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('AI explanation session cleared.'),
                        duration: Duration(seconds: 1),
                      ),
                    );
                  },
                ),

                // Main Scrollable Area
                Expanded(
                  child: productAsync.when(
                    loading: () => const Center(
                      child: CircularProgressIndicator(color: Color(0xFF7C5CE6)),
                    ),
                    error: (err, _) => Center(
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.wifi_off_rounded, size: 48.0, color: Color(0xFF8E8A93)),
                            const SizedBox(height: 12.0),
                            const Text(
                              'Unable to load product context',
                              style: TextStyle(
                                fontFamily: 'Manrope',
                                fontSize: 16.0,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF141414),
                              ),
                            ),
                            const SizedBox(height: 6.0),
                            Text(
                              err.toString(),
                              textAlign: TextAlign.center,
                              style: const TextStyle(fontSize: 12.0, color: Color(0xFF6E6877)),
                            ),
                            const SizedBox(height: 16.0),
                            ElevatedButton(
                              onPressed: () => ref.refresh(productDetailsFamily(widget.barcode)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF7C5CE6),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14.0)),
                              ),
                              child: const Text('Retry', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                            ),
                          ],
                        ),
                      ),
                    ),
                    data: (productDetails) {
                      // Pre-populate with default question if first load
                      if (!_hasInitializedFirstQuestion && chatMessages.isEmpty) {
                        _hasInitializedFirstQuestion = true;
                        WidgetsBinding.instance.addPostFrameCallback((_) {
                          ref.read(aiChatMessagesProvider.notifier).askQuestion(
                                question: 'Is it good for daily consumption?',
                                product: productDetails,
                              );
                        });
                      }

                      return SingleChildScrollView(
                        controller: _scrollController,
                        physics: const BouncingScrollPhysics(),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 6.0),

                            // Section C: Title Header with 3D Sparkle Squircle
                            const AiExplanationHeader(),

                            const SizedBox(height: 14.0),

                            // Section D: Selected Product Context Card
                            AiSelectedProductCard(product: productDetails),

                            const SizedBox(height: 16.0),

                            // Section E: "Try asking" 2x2 Suggestion Grid
                            AiTryAskingGrid(
                              onSelectQuestion: (q) {
                                ref.read(aiChatMessagesProvider.notifier).askQuestion(
                                      question: q,
                                      product: productDetails,
                                    );
                                _scrollToBottom();
                              },
                            ),

                            const SizedBox(height: 14.0),

                            // Section F: Conversation Thread (User bubble + Structured AI Card)
                            AiConversationThread(
                              messages: chatMessages,
                              onRetry: (q) {
                                ref.read(aiChatMessagesProvider.notifier).askQuestion(
                                      question: q,
                                      product: productDetails,
                                    );
                              },
                            ),

                            const SizedBox(height: 16.0),
                          ],
                        ),
                      );
                    },
                  ),
                ),

                // Section G: Docked Bottom Question Input Bar
                productAsync.maybeWhen(
                  data: (productDetails) => AiBottomInputBar(
                    onSubmit: (q) {
                      ref.read(aiChatMessagesProvider.notifier).askQuestion(
                            question: q,
                            product: productDetails,
                          );
                      _scrollToBottom();
                    },
                  ),
                  orElse: () => const SizedBox.shrink(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Custom painter rendering top-right lavender wave matching AI Food Explanation.png
class _AiLavenderWavePainter extends CustomPainter {
  const _AiLavenderWavePainter();

  @override
  void paint(Canvas canvas, Size size) {
    final rect = Rect.fromLTWH(0, 0, size.width, size.height);

    final path = Path();
    path.moveTo(size.width * 0.54, 0);
    path.cubicTo(
      size.width * 0.60,
      size.height * 0.12,
      size.width * 0.40,
      size.height * 0.22,
      size.width * 0.48,
      size.height * 0.38,
    );
    path.cubicTo(
      size.width * 0.56,
      size.height * 0.52,
      size.width * 0.95,
      size.height * 0.56,
      size.width,
      size.height * 0.60,
    );
    path.lineTo(size.width, 0);
    path.close();

    final paint = Paint()
      ..shader = const LinearGradient(
        begin: Alignment.topRight,
        end: Alignment.bottomLeft,
        colors: [
          Color(0xFFD5C6EC),
          Color(0xFFEFE9F8),
          Color(0x00FDF8F4),
        ],
        stops: [0.0, 0.45, 1.0],
      ).createShader(rect);

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
