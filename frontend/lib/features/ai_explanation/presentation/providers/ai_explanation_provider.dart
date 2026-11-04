import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/constants/api_constants.dart';
import '../../../../core/network/api_client.dart';
import '../../../product_details/data/models/product_response_model.dart';
import '../../../product_details/presentation/providers/product_details_provider.dart';
import '../../data/models/ai_explanation_thread_models.dart';

final aiSelectedProductProvider = StateProvider<ProductDetailsResponse?>((ref) => null);

class AiChatNotifier extends StateNotifier<List<AiChatMessage>> {
  final ApiClient _apiClient;

  AiChatNotifier(this._apiClient) : super([]);

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

    try {
      AiStructuredResponse response;
      if (product != null && product.product.barcode.isNotEmpty) {
        try {
          final res = await _apiClient.post(
            ApiConstants.chatEndpoint,
            data: {
              'barcode': product.product.barcode,
              'question': cleanQ,
            },
          );
          final answer = res['answer']?.toString();
          if (answer != null && answer.isNotEmpty) {
            response = AiExplanationEngine.fromBackendAnswer(
              answer: answer,
              product: product,
              question: cleanQ,
            );
          } else {
            response = AiExplanationEngine.generateResponse(
              question: cleanQ,
              product: product,
            );
          }
        } catch (_) {
          // Gracefully fall back to local rule-based explanation
          response = AiExplanationEngine.generateResponse(
            question: cleanQ,
            product: product,
          );
        }
      } else {
        response = AiExplanationEngine.generateResponse(
          question: cleanQ,
          product: product,
        );
      }

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
  final apiClient = ref.watch(apiClientProvider);
  return AiChatNotifier(apiClient);
});
