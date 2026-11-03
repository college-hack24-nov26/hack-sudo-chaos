import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../product_details/data/models/product_response_model.dart';
import '../../data/models/ai_explanation_thread_models.dart';

final aiSelectedProductProvider = StateProvider<ProductDetailsResponse?>((ref) => null);

class AiChatNotifier extends StateNotifier<List<AiChatMessage>> {
  AiChatNotifier() : super([]);

  void resetSession() {
    state = [];
  }

  Future<void> askQuestion({
    required String question,
    required ProductDetailsResponse? product,
  }) async {
    final cleanQ = question.trim();
    if (cleanQ.isEmpty) return;

    final id = DateTime.now().millisecondsSinceEpoch.toString();

    // Add loading message
    final loadingMsg = AiChatMessage(
      id: id,
      question: cleanQ,
      isLoading: true,
      timestamp: DateTime.now(),
    );
    state = [...state, loadingMsg];

    // Simulate realistic async response time (500ms)
    await Future.delayed(const Duration(milliseconds: 500));

    try {
      final response = AiExplanationEngine.generateResponse(
        question: cleanQ,
        product: product,
      );

      final answeredMsg = AiChatMessage(
        id: id,
        question: cleanQ,
        response: response,
        isLoading: false,
        timestamp: DateTime.now(),
      );

      state = [
        for (final m in state)
          if (m.id == id) answeredMsg else m,
      ];
    } catch (e) {
      final errorMsg = AiChatMessage(
        id: id,
        question: cleanQ,
        isLoading: false,
        errorMessage: 'Unable to reach AI explanation engine: $e',
        timestamp: DateTime.now(),
      );

      state = [
        for (final m in state)
          if (m.id == id) errorMsg else m,
      ];
    }
  }
}

final aiChatMessagesProvider =
    StateNotifierProvider<AiChatNotifier, List<AiChatMessage>>((ref) {
  return AiChatNotifier();
});

