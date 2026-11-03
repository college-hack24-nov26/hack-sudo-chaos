# YumSure — Known Limitations and System Boundaries

This document transparently records the architectural boundaries, regulatory caveats, and deliberate design tradeoffs of the YumSure MVP for the hackathon.

---

## 1. Hackathon Scope Constraints (Deliberate Tradeoffs)

1. **No On-Device OCR / Image Recognition**:
   - *Limitation*: The application relies strictly on barcode scanning (EAN-13, EAN-8, UPC) and manual barcode entry. It does not extract text from nutrition tables via camera OCR in this build.
   - *Rationale*: OCR on wrinkled, reflective, curved packaging under uneven retail lighting introduces severe error rates (> 20%). A 24-hour deadline requires prioritising 100% deterministic accuracy over error-prone computer vision.
2. **No Fabricated Overall Health Score**:
   - *Limitation*: Consumers will not see a single "A-F" letter grade or "78/100" health rating.
   - *Rationale*: Composite scores are mathematically subjective, commercially biased, and unscientific. YumSure presents nutrient-specific classifications (Low, Moderate, High) and FSSAI claim validations instead.
3. **Absence of Automated Test Suite**:
   - *Limitation*: In adherence to project development constraints, automated testing suites (pytest, flutter_test) are omitted.
   - *Mitigation*: Runtime verification is conducted manually against real-world Indian packaged goods across all deterministic engines.

---

## 2. Regulatory & Data Inherent Limitations

1. **Transition Period for "Added Sugars" on Indian Labels**:
   - Under older packaging compliance batches, some Indian food packages declared only "Total Carbohydrates" and "of which Sugars", without segregating "Added Sugars".
   - *Handling*: When `added_sugars` is not explicitly declared on the label, YumSure records the nutrient status as `NOT_DECLARED`. It evaluates claims using `total_sugars` where allowed and explicitly informs the user that added sugar breakdown was not declared by the manufacturer.
2. **Open Food Facts Indian Catalog Coverage**:
   - Open Food Facts has extensive coverage of major metropolitan packaged goods (Britannia, Parle, ITC, Amul, Nestlé India, Haldiram's). However, hyper-local or regional snacks (e.g., local state namkeen brands) may not yet be indexed in OFF.
   - *Handling*: When a barcode returns HTTP 404, the application displays a clear "Product Not Yet Cataloged" message rather than crashing or guessing values.
3. **Draft Front-of-Pack Labelling (FOPL / INR)**:
   - FSSAI has issued draft notifications regarding star ratings and Front-of-Pack warning labels, but final mandatory implementation has experienced multiple stakeholder iterations.
   - *Handling*: YumSure restricts claim verifications strictly to gazetted, currently enforceable regulations: **FSSAI (Advertising and Claims) Regulations, 2018** and **FSSAI (Labelling and Display) Regulations, 2020**.

---

## 3. Network & AI Availability Dependencies

1. **External LLM Latency & Connectivity**:
   - Generating plain-English AI explanations via Grok (xAI) or NVIDIA NIM requires an outbound HTTPS request (~1.2 - 2.5 seconds latency).
   - *Mitigation*: The app caches generated explanations in PostgreSQL. Furthermore, if the AI provider is offline or throttled (HTTP 429), YumSure activates an immediate local deterministic template explainer that operates in zero milliseconds without external dependencies.
2. **Serving Size Discrepancies**:
   - FSSAI regulations allow manufacturers to determine their own serving sizes. A manufacturer might declare a 15g serving size for a 100g biscuit pack to make sodium and calorie numbers appear lower on the front panel.
   - *Mitigation*: YumSure normalizes all nutrient values and classifications to **per 100g / per 100ml** as the primary scientific standard, while providing the per-serving calculation as secondary information.

