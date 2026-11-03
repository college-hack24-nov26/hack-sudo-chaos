import 'package:flutter/material.dart';

class AiBottomInputBar extends StatefulWidget {
  final ValueChanged<String> onSubmit;
  final bool isEnabled;

  const AiBottomInputBar({
    super.key,
    required this.onSubmit,
    this.isEnabled = true,
  });

  @override
  State<AiBottomInputBar> createState() => _AiBottomInputBarState();
}

class _AiBottomInputBarState extends State<AiBottomInputBar> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _handleSend() {
    final text = _controller.text.trim();
    if (text.isNotEmpty && widget.isEnabled) {
      widget.onSubmit(text);
      _controller.clear();
      FocusScope.of(context).unfocus();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16.0, 6.0, 16.0, 14.0),
      padding: const EdgeInsets.symmetric(horizontal: 10.0, vertical: 8.0),
      decoration: BoxDecoration(
        color: const Color(0xFFFAF7F5),
        borderRadius: BorderRadius.circular(30.0),
        border: Border.all(color: Colors.white, width: 1.5),
        boxShadow: const [
          BoxShadow(
            color: Color(0x12000000),
            blurRadius: 18.0,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        children: [
          // Expanded Text Field Pill
          Expanded(
            child: Container(
              height: 44.0,
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              decoration: BoxDecoration(
                color: const Color(0xFFF1ECE9),
                borderRadius: BorderRadius.circular(22.0),
              ),
              alignment: Alignment.center,
              child: TextField(
                controller: _controller,
                enabled: widget.isEnabled,
                onSubmitted: (_) => _handleSend(),
                decoration: const InputDecoration(
                  hintText: 'Ask another question...',
                  hintStyle: TextStyle(
                    fontFamily: 'Manrope',
                    fontSize: 14.0,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFF68636E),
                  ),
                  border: InputBorder.none,
                  isDense: true,
                  contentPadding: EdgeInsets.zero,
                ),
                style: const TextStyle(
                  fontFamily: 'Manrope',
                  fontSize: 14.0,
                  color: Color(0xFF141414),
                ),
              ),
            ),
          ),

          const SizedBox(width: 10.0),

          // Circular Send Button (44x44)
          GestureDetector(
            onTap: _handleSend,
            child: Container(
              width: 44.0,
              height: 44.0,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF9E82F2),
                    Color(0xFF7C5CE6),
                  ],
                ),
                border: Border.all(color: Colors.white, width: 1.5),
                boxShadow: const [
                  BoxShadow(
                    color: Color(0x337C5CE6),
                    blurRadius: 10.0,
                    offset: Offset(0, 4),
                  ),
                ],
              ),
              alignment: Alignment.center,
              child: const Icon(
                Icons.send_rounded,
                size: 20.0,
                color: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

