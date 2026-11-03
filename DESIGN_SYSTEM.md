# YumSure — Frontend Design System & Visual Specification

This document details the visual tokens, typography, component styling, and performance guidelines for the YumSure mobile client across all screens.

---

## 1. Aesthetic Identity & Design Philosophy

YumSure adopts a warm, editorial, consumer-trust design language inspired by modern health-intelligence applications.

### Core Principles
- **Warm Canvas**: Built upon a warm ivory/cream background (`#FBF8F5`) rather than harsh clinical white or generic Material grey.
- **Subtle Accents**: Soft pastel peach (`#FFD8CC`) and gentle lavender (`#E8DEF8`) provide visual breathing room.
- **Lightweight Alternative to Glassmorphism**:
  - The design references exhibit frosted, translucent surfaces.
  - **Budget Android Performance Rule**: To guarantee 60-120 FPS on entry-level Android devices, heavy `BackdropFilter` and nested blur layers are strictly prohibited.
  - Instead, surfaces use solid white cards (`#FFFFFF`) with ultra-fine border lines (`#EFE8E1`), soft tinting, and static gradients.
- **Restrained Shadows**: Elevations are kept to zero or subtle border outlines, eliminating GPU-heavy shadow rendering passes during scrolling.

---

## 2. Design Tokens

### 2.1 Color Palette

| Token | Hex Value | Usage Role |
| :--- | :--- | :--- |
| `background` | `#FBF8F5` | Primary screen canvas background (warm cream) |
| `surfaceCard` | `#FFFFFF` | Rounded cards for nutrient panels, identity, and list items |
| `surfaceSubtle` | `#F7F3EE` | Thumbnail backgrounds and subtle unselected buttons |
| `textPrimary` | `#191B1F` | High-contrast dark navy text for headings and values |
| `textSecondary` | `#6B7280` | Subtitles, measurement units, and explanations |
| `textTertiary` | `#9CA3AF` | Placeholder icons, disabled controls |
| `brandOrange` | `#FF7A45` | YumSure logo smile, hero highlights, active loaders |
| `accentDark` | `#1E222B` | Selected toggle pills and primary action buttons |
| `accentPeach` | `#FFD8CC` | Border ring on hero scan button |
| `accentLavender` | `#E8DEF8` | Highlight oval for active bottom navigation tab |
| `accentLavenderLight` | `#F5EEFD` | Subtle background tint for AI tags |
| `accentPurple` | `#7C3AED` | AI Explanation tags and comparison icons |
| `border` | `#EFE8E1` | Standard card border stroke (1.0 dp) |
| `borderSubtle` | `#F5EFE9` | Subtle inner dividers and badge outlines |

### 2.2 Nutritional Interpretation Colors (Consistent System-Wide)

| Semantic Level | Text / Icon Color | Background Tint | Border Stroke | Meaning / Threshold |
| :--- | :--- | :--- | :--- | :--- |
| **Low / Good** | `#16A34A` (Green) | `#DCFCE7` | `#86EFAC` | Low sugar/sodium/fat or high protein/fibre |
| **Moderate** | `#F59E0B` (Amber) | `#FEF3C7` | `#FCD34D` | Medium density, check overall daily balance |
| **High / Concern** | `#EF4444` (Red) | `#FEE2E2` | `#FCA5A5` | Exceeds healthy threshold for negative nutrients |
| **Neutral / Info** | `#3B82F6` (Blue) | `#DBEAFE` | `#93C5FD` | Informational nutrient (e.g. Energy, Carbs) |
| **Unclassified** | `#64748B` (Slate) | `#F1F5F9` | `#E2E8F0` | Non-classifiable or missing statutory standard |

---

## 3. Typography Scale

- **Display**: 28sp / Bold / Line-height 1.2 / Letter-spacing -0.5 (Brand Title)
- **H1**: 22sp / Bold / Line-height 1.25 / Letter-spacing -0.3 (Major Screen Headers)
- **H2**: 18sp / Bold / Line-height 1.3 / Letter-spacing -0.2 (Section Titles, Product Name)
- **H3**: 16sp / Semi-Bold / Line-height 1.35 (Card Headers, Nutrient Names)
- **Body Large**: 15sp / Regular / Line-height 1.4 (Primary descriptive text)
- **Body Medium**: 13.5sp / Regular / Line-height 1.4 (Secondary subtitles, brand names)
- **Body Small**: 12sp / Regular / Line-height 1.35 (Nutrient explanations, statutory footnotes)
- **Label / Button**: 11.5sp / Semi-Bold / Letter-spacing 0.2 (Selector pills, badges)
- **Value Large**: 22sp / Extra-Bold / Letter-spacing -0.5 (Energy hero display)
- **Value Medium**: 15sp / Bold (Nutrient quantities)

---

## 4. Spacing, Geometry & Iconography

- **Base Grid**: 4dp incremental scale (xs: 4dp, sm: 8dp, md: 12dp, lg: 16dp, xl: 20dp, xxl: 24dp, xxxl: 32dp).
- **Card Radius**: `18.0dp` with a `1.0dp` stroke of `AppColors.border`.
- **Hero Card Radius**: `26.0dp` with a floating action circle.
- **Pill Radius**: `999.0dp` for measurement selectors, bottom navigation bar, and action buttons.
- **Icon Sizing**:
  - `iconSm`: 16dp (finding bullets, badge indicators)
  - `iconMd`: 20dp (app bar actions, category icons, bottom navigation icons)
  - `iconLg`: 24dp (navigation items, category icons)
  - `iconXl`: 32dp (error & placeholder graphics)

---

## 5. Home Screen Component Specifications

1. **Brand Header (`HomeHeader`)**:
   - Clean, lightweight horizontal layout.
   - Text "YumSure" with curved orange underline.
   - Action icon on the right in a 42x42dp rounded card (`Icons.grid_view_rounded`) with clear tooltip "Browse all categories" navigating to `/search`.
2. **Scan Product Hero Card (`ScanProductHeroCard`)**:
   - Translucent-looking gradient with warm peach, neutral grey and soft lavender tones (`[#C4988B, #88788D, #5A4F62, #7E7395, #A597BA]`).
   - Center graphic: Barcode brackets with stylized crisp white bars.
   - Centered 60x60dp white floating circle with scan crosshairs icon (`Icons.filter_center_focus_rounded`) and peach border (`#FFD8CC`), overlapping the bottom edge.
3. **Explore Categories (`ExploreCategoriesSection`)**:
   - 4 horizontal cards (Snacks, Beverages, Biscuits, Dairy) featuring curated, single-subject photography cropped to 300x360 with subtle dark gradient overlays for razor-sharp label readability.
   - Rounded corners (18dp) with elevation shadow.
4. **Your Scan Insights (`ScanInsightsSection`)**:
   - Timeframe selector popup menu (`7d`, `30d`, `all`).
   - Editorial warm peach/cream card (`#FFF6F0` to `#FAEBE3`) with coral bar chart container (`#FFDDD2`), bold dark title, grey supporting text, and circular white arrow button.
   - Distinct handling for HTTP 200 with data, HTTP 200 with `{"insight": null}` (legitimate empty state), and compact error state.
5. **Recent Scans (`RecentScansSection`)**:
   - Stacked card list matching reference: rounded corners 18dp, product image, title, relative time, badge, and navigation chevron.
   - Compact connection status banner (`_RecentScansCompactErrorCard`) when offline with inline retry action, without occupying the entire section.
   - Clean first-scan empty state when `scans.isEmpty` under HTTP 200.
   - Product list with thumbnail (or neutral placeholder), relative timestamp, and severity finding badge.
   - Guaranteed empty state when no scan history exists.
6. **Bottom Navigation (`YumSureBottomNavBar`)**:
   - 3-tab floating pill bar (Home, Search, Saved).
   - Lavender oval pill highlight for active tab.
