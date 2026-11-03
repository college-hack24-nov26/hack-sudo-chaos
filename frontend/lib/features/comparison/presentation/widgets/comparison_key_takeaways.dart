import 'package:flutter/material.dart';
import '../../data/models/comparison_models.dart';

class ComparisonKeyTakeaways extends StatelessWidget {
  final List<ComparisonTakeaway> takeaways;

  const ComparisonKeyTakeaways({
    super.key,
    required this.takeaways,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Heading
          const Text(
            'Key Takeaways',
            style: TextStyle(
              fontFamily: 'Manrope',
              fontSize: 17.0,
              fontWeight: FontWeight.w800,
              letterSpacing: -0.3,
              color: Color(0xFF141414),
            ),
          ),

          const SizedBox(height: 12.0),

          // Card Container
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14.0, vertical: 12.0),
            decoration: BoxDecoration(
              color: const Color(0xFFF8F4F9),
              borderRadius: BorderRadius.circular(22.0),
              border: Border.all(color: Colors.white, width: 1.5),
              boxShadow: const [
                BoxShadow(
                  color: Color(0x08000000),
                  blurRadius: 10.0,
                  offset: Offset(0, 3),
                ),
              ],
            ),
            child: ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: takeaways.length,
              separatorBuilder: (context, index) => const SizedBox(height: 10.0),
              itemBuilder: (context, index) {
                final takeaway = takeaways[index];
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Icon
                    if (takeaway.iconBgColor != null)
                      Container(
                        width: 20.0,
                        height: 20.0,
                        decoration: BoxDecoration(
                          color: takeaway.iconBgColor,
                          shape: BoxShape.circle,
                        ),
                        alignment: Alignment.center,
                        child: Icon(
                          takeaway.icon,
                          size: 14.0,
                          color: takeaway.iconColor,
                        ),
                      )
                    else
                      Icon(
                        takeaway.icon,
                        size: 20.0,
                        color: takeaway.iconColor,
                      ),

                    const SizedBox(width: 10.0),

                    // RichText
                    Expanded(
                      child: RichText(
                        text: TextSpan(
                          style: const TextStyle(
                            fontFamily: 'Manrope',
                            fontSize: 12.5,
                            color: Color(0xFF222026),
                            height: 1.35,
                          ),
                          children: [
                            TextSpan(
                              text: '${takeaway.boldSubject} ',
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            TextSpan(
                              text: takeaway.text,
                              style: const TextStyle(
                                fontWeight: FontWeight.w400,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

