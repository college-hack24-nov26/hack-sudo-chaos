# YumSure — Frontend Implementation Report (Phase 2: Home Screen)

This document describes the architectural layout, widget responsibilities, state management, route correction, and Android execution instructions for the Flutter client after completing **Phase 2: Home Screen Implementation**.

---

## 1. Project Overview & Scope

Phase 2 delivers the production-ready **Home Screen** (`/home`), precisely reproducing the visual layout and information hierarchy from [`design_references/home_reference.png`](file:///d:/hack-sudo-chaos/design_references/home_reference.png).

- **Framework**: Flutter 3.32.8 (Channel stable)
- **Dart SDK**: 3.8.1
- **State Management**: `flutter_riverpod: ^2.6.1`
- **Routing**: `go_router: ^14.8.1`
- **Networking**: `dio: ^5.11.1`
- **Initial Route Correction**: Fresh app launch now opens `/home` instead of a hardcoded product barcode.

---

## 2. Directory & Component Architecture

```
frontend/lib/
├── main.dart                               # Entry point with ProviderScope
├── app/
│   ├── app.dart                            # YumSureApp MaterialApp.router configuration
│   ├── router/
│   │   └── app_router.dart                 # Initial route: /home; routes for home, product, search, scanner, saved
│   └── theme/
│       ├── app_colors.dart                 # Centralized design tokens (warm cream, peach, lavender, dark navy)
│       ├── app_spacing.dart                # 4dp spacing grid, radii (cards 18dp, pills 999dp)
│       ├── app_typography.dart             # Editorial font hierarchy
│       └── app_theme.dart                  # Material 3 light theme definition
├── core/
│   ├── config/env_config.dart              # Dynamic host resolution (10.0.2.2 for Android emulator)
│   ├── constants/api_constants.dart        # Route endpoints (/api/v1/products, /api/v1/history)
│   └── network/
│       ├── api_client.dart                 # Dio client with custom headers & timeouts
│       └── api_exceptions.dart             # Typed exception classes
├── features/
│   ├── home/
│   │   ├── data/
│   │   │   ├── models/
│   │   │   │   └── home_models.dart        # ScanHistoryItem, ScanInsight, CategoryItem
│   │   │   └── repositories/
│   │   │       └── home_repository.dart    # HomeRepository interface & API implementation
│   │   └── presentation/
│   │       ├── providers/
│   │       │   └── home_provider.dart      # Riverpod providers (recentScans, insights, timeframe, categories)
│   │       ├── screens/
│   │       │   └── home_screen.dart        # Complete Home Screen assembly (Sections A-E + Bottom Nav)
│   │       └── widgets/
│   │           ├── home_header.dart        # Section A: Brand logo with orange smile & grid icon
│   │           ├── scan_product_hero_card.dart # Section B: Barcode hero card with floating scan circle
│   │           ├── explore_categories_section.dart # Section C: 4 horizontal category cards (Snacks, Drinks, Biscuits, Dairy)
│   │           ├── scan_insights_section.dart  # Section D: Timeframe selector (7d/30d/all) & insight or empty state
│   │           └── recent_scans_section.dart   # Section E: Scanned product cards with severity badges or empty state
│   ├── product_details/                    # Phase 1: Complete 10-section Nutrition Visualization Screen
│   ├── search/presentation/screens/search_placeholder_screen.dart # Connected to bottom nav tab 1
│   ├── scanner/presentation/screens/scanner_placeholder_screen.dart # Destination for hero scan button
│   ├── saved/presentation/screens/saved_placeholder_screen.dart   # Connected to bottom nav tab 2
│   ├── comparison/presentation/screens/comparison_placeholder_screen.dart
│   ├── ingredients/presentation/screens/ingredients_placeholder_screen.dart
│   └── ai_explanation/presentation/screens/ai_explanation_placeholder_screen.dart
└── shared/
    └── widgets/
        ├── yumsure_app_bar.dart             # Shared top app bar
        └── yumsure_bottom_nav_bar.dart     # Floating bottom navigation bar (Home, Search, Saved)
```

---

## 3. Section-by-Section Implementation Review

| Section | Widget Name | Key Responsibilities | Design Reference Match |
| :--- | :--- | :--- | :--- |
| **Aurora Background** | `_AuroraBackgroundPainter` | Static `CustomPainter` rendering warm ivory canvas (`#FAF4EF`), diagonal sweeping lavender planes (`#D6C8F4`), diagonal warm-ivory wave, prominent spherical peach/orange orb entering from the left (`#FE873E`), and lower amber glow. Zero runtime blur cost. | Matches distinctive abstract composition of `home_reference.png` |
| **A. Brand Header** | `HomeHeader` | Displays bold "YumSure" brand text (`Manrope` 800) with signature curved orange smile accent and a defined 42x42dp rounded button on the right navigating to `/search` (Browse all categories). | Matches top bar of `home_reference.png` |
| **B. Scan Product Hero** | `ScanProductHeroCard` | Floating premium interface element with five-stop translucent-looking gradient (`[#CF9C8F, #918095, #5A4D62, #7E7295, #A89BBF]`), top-edge light reflection rim (1.2dp), subtle inner border (22dp radius), prominent barcode bracket graphic (`72×48dp`), bold `Manrope` typography, and polished 62×62dp circular scan action button overlapping the bottom edge. Tapping opens `/scanner`. | Matches luminous hero card of `home_reference.png` |
| **C. Explore Categories** | `ExploreCategoriesSection` | Responsive 4-card row layout: all 4 categories (Snacks, Beverages, Biscuits, Dairy) fit 100% on screen simultaneously with zero clipping of Dairy. Curated single-subject studio photography cropped to 300x380, rounded corners (16dp), bottom dark gradient overlays, and crisp white `Manrope` labels. | Matches curated photography row of `home_reference.png` |
| **D. Your Scan Insights** | `ScanInsightsSection` | Displays title with timeframe dropdown. Reusable editorial banner (`#FFF6F0` to `#FAEBE3`, border `#F0DDD4`): when actual data is present, renders bar chart in coral container (`#FFDDD2`), dark headline, supporting text, and circular arrow button. When backend is offline, preserves exact same editorial banner geometry with connection status and retry action. Never invents data. | Matches editorial insights card of `home_reference.png` |
| **E. Recent Scans** | `RecentScansSection` | Distinct presentations: (A) stacked cards with product image, title, category, relative timestamp, and finding badge; (B) clean first-scan empty state with "No scans yet" and primary scan action button; (C) subtle non-intrusive single-line connection status with inline retry. | Matches stacked recent scans list of `home_reference.png` |
| **Bottom Navigation** | `YumSureBottomNavBar` | Floating rounded white pill navigation bar with 3 tabs: Home, Search, Saved. Selected tab displays soft lavender highlight pill (`AppColors.accentLavender`). Maintains bottom SafeArea. | Matches bottom navigation bar of `home_reference.png` |

---

## 4. Initial Route Correction

- **Previous State**: Router opened `/product/8901030383701` on launch, incorrectly bypassing Home and forcing a hardcoded barcode lookup.
- **Current State**:
  - `initialLocation`: `AppRoutes.home` (`/home`).
  - Root route `/`: Redirects immediately to `/home`.
  - Product Details (`/product/:barcode`) is only pushed when the user selects a product from Recent Scans or scans a barcode.
  - Zero hardcoded products are requested on launch.

---

## 5. Strict Zero-Fabrication & Empty-State Behavior

YumSure enforces strict scientific and regulatory integrity:

1. **Scan Insights**:
   - Never uses fabricated statistics or hardcoded counts.
   - If user has no scan history or backend returns no data, renders:
     > *"Your food insights will appear here after you scan products."*
     With an actionable **Scan Product** button that opens `/scanner`.
2. **Recent Scans**:
   - Does not populate dummy Lay's, Maggi, or Coca-Cola products.
   - If user has no scan history, renders:
     > *"No scans yet."*
     > *"Scan your first packaged product to start understanding what is inside."*
     With an actionable **Scan a Product** button.

---

## 6. Android Execution Instructions

```powershell
# 1. Navigate to frontend directory
cd D:\hack-sudo-chaos\frontend

# 2. Check connected Android devices or emulators
flutter devices

# 3. Launch application on Android (starts directly on /home)
flutter run -d android

# (Optional) If running against backend host IP on local Wi-Fi:
flutter run -d android --dart-define=API_BASE_URL=http://<YOUR_HOST_IP>:8000
```
