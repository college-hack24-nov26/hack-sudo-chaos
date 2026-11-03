import 'package:flutter/material.dart';
import '../../data/models/ai_explanation_thread_models.dart';

class AiConversationThread extends StatelessWidget {
  final List<AiChatMessage> messages;
  final ValueChanged<String>? onRetry;

  const AiConversationThread({
    super.key,
    required this.messages,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    if (messages.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: messages.length,
        separatorBuilder: (_, __) => const SizedBox(height: 20.0),
        itemBuilder: (context, index) {
          final message = messages[index];
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. User Question Row (Right-Aligned)
              _buildUserBubble(message.question),

              const SizedBox(height: 12.0),

              // 2. Structured AI Response Card
              _buildAiResponseCard(context, message),
            ],
          );
        },
      ),
    );
  }

  Widget _buildUserBubble(String question) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.end,
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        Flexible(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 10.0),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(20.0),
              gradient: const LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFFEAE0F9),
                  Color(0xFFDECFF6),
                ],
              ),
              border: Border.all(color: Colors.white, width: 1.2),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x0C000000),
                  blurRadius: 8.0,
                  offset: Offset(0, 2),
                ),
              ],
            ),
            child: Text(
              question,
              style: const TextStyle(
                fontFamily: 'Manrope',
                fontSize: 13.5,
                fontWeight: FontWeight.w600,
                color: Color(0xFF18151E),
                height: 1.3,
              ),
            ),
          ),
        ),

        const SizedBox(width: 8.0),

        // User Avatar (36x36)
        Container(
          width: 36.0,
          height: 36.0,
          decoration: BoxDecoration(
            color: const Color(0xFFEDE6F8),
            shape: BoxShape.circle,
            border: Border.all(color: Colors.white, width: 1.5),
            boxShadow: const [
              BoxShadow(
                color: Color(0x105A4382),
                blurRadius: 6.0,
                offset: Offset(0, 2),
              ),
            ],
          ),
          alignment: Alignment.center,
          child: const Icon(
            Icons.person_outline_rounded,
            size: 20.0,
            color: Color(0xFF6B4CE6),
          ),
        ),
      ],
    );
  }

  Widget _buildAiResponseCard(BuildContext context, AiChatMessage msg) {
    return Container(
      padding: const EdgeInsets.all(16.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF7F5),
        borderRadius: BorderRadius.circular(26.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x0D000000),
            blurRadius: 16.0,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: msg.isLoading
          ? _buildLoadingState()
          : (msg.errorMessage != null
              ? _buildErrorState(msg)
              : _buildStructuredContent(msg.response!)),
    );
  }

  Widget _buildLoadingState() {
    return const Padding(
      padding: EdgeInsets.symmetric(vertical: 24.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 20.0,
            height: 20.0,
            child: CircularProgressIndicator(
              strokeWidth: 2.5,
              color: Color(0xFF7C5CE6),
            ),
          ),
          SizedBox(width: 14.0),
          Text(
            'Analyzing product facts with YumSure AI...',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 13.0,
              fontWeight: FontWeight.w600,
              color: Color(0xFF5A5560),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(AiChatMessage msg) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12.0),
      child: Column(
        children: [
          const Icon(Icons.cloud_off_rounded, size: 36.0, color: Color(0xFFD97E26)),
          const SizedBox(height: 8.0),
          const Text(
            'AI explanation temporarily unavailable',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 14.0,
              fontWeight: FontWeight.w700,
              color: Color(0xFF141414),
            ),
          ),
          const SizedBox(height: 4.0),
          Text(
            msg.errorMessage ?? 'Offline or network failure.',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 12.0, color: Color(0xFF6E6877)),
          ),
          const SizedBox(height: 12.0),
          if (onRetry != null)
            ElevatedButton(
              onPressed: () => onRetry!(msg.question),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF7C5CE6),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14.0)),
              ),
              child: const Text('Retry', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
            ),
        ],
      ),
    );
  }

  Widget _buildStructuredContent(AiStructuredResponse resp) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Top Direct Answer Row
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Left Sparkle Circle (34x34)
            Container(
              width: 34.0,
              height: 34.0,
              decoration: BoxDecoration(
                color: const Color(0xFFE5DAFA),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 1.0),
              ),
              alignment: Alignment.center,
              child: const Icon(
                Icons.auto_awesome,
                size: 18.0,
                color: Color(0xFF6B4CE6),
              ),
            ),

            const SizedBox(width: 12.0),

            // Right RichText
            Expanded(
              child: RichText(
                text: TextSpan(
                  style: const TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 13.8,
                    color: Color(0xFF221E28),
                    height: 1.38,
                  ),
                  children: [
                    TextSpan(
                      text: '${resp.boldConclusion} ',
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF141414),
                      ),
                    ),
                    TextSpan(
                      text: resp.bodyText,
                      style: const TextStyle(
                        fontWeight: FontWeight.w400,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),

        // Divider
        const Padding(
          padding: EdgeInsets.symmetric(vertical: 12.0),
          child: Divider(height: 1.0, color: Color(0xFFEDE8E4)),
        ),

        // "Key Reasons" Section
        if (resp.keyReasons.isNotEmpty) ...[
          const Text(
            'Key Reasons',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 15.5,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.2,
              color: Color(0xFF141414),
            ),
          ),
          const SizedBox(height: 8.0),
          ...resp.keyReasons.map((r) => _buildReasonRow(r)),
        ],

        // "In Short" Split Banner
        Container(
          margin: const EdgeInsets.only(top: 14.0),
          padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(18.0),
            gradient: const LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                Color(0xFFF5F0FC),
                Color(0xFFE8D9FA),
              ],
            ),
            border: Border.all(color: Colors.white, width: 1.2),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // Left Lightbulb Icon + "In Short"
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 30.0,
                    height: 30.0,
                    decoration: const BoxDecoration(
                      color: Color(0xFFFDF3E2),
                      shape: BoxShape.circle,
                    ),
                    alignment: Alignment.center,
                    child: const Icon(
                      Icons.lightbulb_outline_rounded,
                      size: 18.0,
                      color: Color(0xFFE68A1E),
                    ),
                  ),
                  const SizedBox(width: 8.0),
                  const Text(
                    'In Short',
                    style: TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 14.0,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF141414),
                    ),
                  ),
                ],
              ),

              // Divider
              Container(
                width: 1.0,
                height: 30.0,
                color: const Color(0xFFCDC2DF),
                margin: const EdgeInsets.symmetric(horizontal: 12.0),
              ),

              // Right Summary
              Expanded(
                child: Text(
                  resp.inShort,
                  style: const TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 12.2,
                    fontWeight: FontWeight.w500,
                    height: 1.35,
                    color: Color(0xFF1E1B24),
                  ),
                ),
              ),
            ],
          ),
        ),

        // Bottom Regulatory Disclaimer Bar
        Container(
          margin: const EdgeInsets.only(top: 10.0),
          padding: const EdgeInsets.symmetric(horizontal: 12.0, vertical: 10.0),
          decoration: BoxDecoration(
            color: const Color(0xFFF4F1EE),
            borderRadius: BorderRadius.circular(14.0),
          ),
          child: const Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.info_outline_rounded,
                size: 18.0,
                color: Color(0xFF4A454E),
              ),
              SizedBox(width: 8.0),
              Expanded(
                child: Text(
                  'This explanation is based on the nutrition and ingredient information available for this product and general dietary guidance (FSSAI).',
                  style: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 11.2,
                    fontWeight: FontWeight.w400,
                    height: 1.32,
                    color: Color(0xFF4A454E),
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildReasonRow(AiKeyReason r) {
    return Padding(
      padding: const EdgeInsets.only(top: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          // Left Pill (width: 124, height: 36)
          Container(
            width: 124.0,
            height: 36.0,
            padding: const EdgeInsets.symmetric(horizontal: 8.0),
            decoration: BoxDecoration(
              color: r.pillBackgroundColor,
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: Row(
              children: [
                Icon(r.icon, size: 17.0, color: r.pillTextColor),
                const SizedBox(width: 6.0),
                Expanded(
                  child: Text(
                    r.valueText != null ? '${r.label} (${r.valueText})' : r.label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontFamily: 'Manrope',
                      fontSize: 11.5,
                      fontWeight: FontWeight.w700,
                      color: r.pillTextColor,
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Center Vertical Divider
          Container(
            width: 1.0,
            height: 32.0,
            color: const Color(0xFFE6E1DC),
            margin: const EdgeInsets.symmetric(horizontal: 12.0),
          ),

          // Right Factual Explanation
          Expanded(
            child: Text(
              r.explanation,
              style: const TextStyle(
                fontFamily: 'Manrope',
                fontSize: 12.2,
                fontWeight: FontWeight.w400,
                height: 1.35,
                color: Color(0xFF1E1B24),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

