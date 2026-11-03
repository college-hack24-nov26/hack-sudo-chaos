# YumSure — Frontend-to-Backend API Integration Specification

This document details the HTTP client implementation, request/response models, environment configuration, error recovery, and the strict distinction between legitimate empty data, HTTP errors, and malformed responses.

---

## 1. Environment & Network Architecture

### 1.1 Base URL Routing Strategy
Because Android emulators cannot access host `localhost:8000` directly, `EnvConfig` automatically selects the appropriate network interface:

| Environment | Host Address | Rationale |
| :--- | :--- | :--- |
| **Android Emulator** | `http://10.0.2.2:8000` | Standard Android Studio loopback router to the development PC |
| **Physical Android Device** | `--dart-define=API_BASE_URL=http://<PC_LOCAL_IP>:8000` | Overridable at compile/run time |
| **Desktop / Web** | `http://127.0.0.1:8000` | Localhost direct loopback |

### 1.2 HTTP Client (`Dio`)
- **Connect Timeout**: 8.0 seconds
- **Receive Timeout**: 10.0 seconds
- **User-Agent**: `YumSure-Flutter/1.0.0 (Android; client)`
- **Content-Type**: `application/json`

---

## 2. API Contracts & Strict Validation Rules

### 2.1 Product Nutrition Intelligence: `GET /api/v1/products/{barcode}`
- **Method**: `GET`
- **Path**: `/api/v1/products/{barcode}`
- **Query Parameters**: `include_ai_explanation` (bool, default: `true`)
- **Mapped In**: `ProductRepository.getProductByBarcode()`
- **Response**: `ProductDetailsResponse`
- **404 Behavior**: Throws `ProductNotFoundException(barcode: ...)`, triggering the "Product Not Found" screen.

### 2.2 Scan History: `GET /api/v1/history`
- **Method**: `GET`
- **Path**: `/api/v1/history`
- **Query Parameters**: `limit` (int, default: 5)
- **Response Schema**:
```json
{
  "total_scans": 12,
  "items": [
    {
      "barcode": "8901030383701",
      "product_name": "NutriChoice Digestive Biscuits",
      "brand_name": "Britannia",
      "food_category": "Biscuits",
      "image_url": "https://...",
      "scanned_at": "2026-11-03T18:30:00Z",
      "key_finding": "Higher sugar",
      "key_finding_severity": "HIGH"
    }
  ]
}
```
- **Strict Response Validation in `HomeRepositoryImpl`**:
  1. The response JSON **must** contain an `'items'` key. If missing, throws `InvalidResponseException`.
  2. The `'items'` field **must not be null**. If null, throws `InvalidResponseException`.
  3. The `'items'` field **must be a `List`**. If another type, throws `InvalidResponseException`.
  4. Each element in `'items'` **must be a JSON object (`Map<String, dynamic>`)**.
  5. **Empty State Rule**: `HomeRepositoryImpl` returns `const []` **only when the backend explicitly returns `{"items": []}`**. It does **not** convert null, missing keys, or malformed JSON into an empty state.

### 2.3 Scan Insights: `GET /api/v1/history/insights`
- **Method**: `GET`
- **Path**: `/api/v1/history/insights`
- **Query Parameters**: `timeframe` (string: `'7d'`, `'30d'`, `'all'`)
- **Response Schema**:
```json
{
  "insight": {
    "title": "High Sodium",
    "description": "2 of your 5 scanned products were high in sodium.",
    "affected_count": 2,
    "total_scanned_count": 5,
    "finding_type": "high_sodium",
    "timeframe": "7d"
  }
}
```
- **Strict Response Validation in `HomeRepositoryImpl`**:
  1. The response JSON **must** contain an `'insight'` key. If missing, throws `InvalidResponseException`.
  2. **Legitimate Empty State**: If the backend explicitly returns `{"insight": null}`, returns `null` (rendering the *"Your food insights will appear here after you scan products"* prompt).
  3. If present and non-null, the `'insight'` field **must be a `Map<String, dynamic>`**. If another type, throws `InvalidResponseException`.

---

## 3. Strict HTTP Status & Error Separation Matrix

`HomeRepositoryImpl` and `ApiClient` enforce a strict separation of HTTP states:

| HTTP Status / Condition | Exception Thrown | Repository Behavior | UI Presentation |
| :--- | :--- | :--- | :--- |
| **HTTP 200 (Explicit Empty Data)** | *None (Success)* | Returns `const []` only for `{"items": []}` or `null` for `{"insight": null}`. | **Legitimate Empty State**: Displays *"No scans yet"* or *"Your food insights will appear here after you scan products"* with a "Scan Product" action. |
| **HTTP 200 (Malformed / Missing Keys)** | `InvalidResponseException` | Throws `InvalidResponseException`. Never returns `[]`. | **Invalid Response Structure**: Displays structured parsing error notice with a retry action. |
| **HTTP 404 (Not Found)** | `NotFoundException` | Rethrows `NotFoundException`. Never returns `[]`. | **Endpoint Not Available (404)**: Informs user that the requested endpoint was not found on the server. |
| **HTTP 500 (Server Error)** | `ServerException` | Rethrows `ServerException`. Never returns `[]`. | **Server Error (500)**: Displays backend error details with a "Try Again" retry action. |
| **Network Failure / Offline** | `NetworkException` | Rethrows `NetworkException`. Never returns `[]`. | **Connection Failed**: Informs user that host is unreachable or connection timed out, with a "Try Again" retry action. |

---

## 4. Strict Missing-Data & Zero-Substitution Rules

The frontend strictly obeys the project's data integrity rules:

1. **No Silent Zeroing**: If nutrient values are null, the UI displays `'—'` (em-dash). It **never** displays `0 g`.
2. **Missing Serving Size**: If serving size is null or zero, the "Per serving" toggle is automatically disabled with an explanatory note.
3. **Threshold Indicators**: The 3-tier colored progress bar only renders if all three threshold values are provided by the backend.
4. **Allergens**: If the allergen list is empty, the UI displays an explicit warning. It never claims the product is allergen-free.
5. **No Fake / Dummy Data**: Insights and recent scans are never populated with hardcoded values.
