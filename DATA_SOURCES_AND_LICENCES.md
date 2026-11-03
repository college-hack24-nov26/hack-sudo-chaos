# YumSure — Data Sources, Licensing, and Compliance Ledger

This document establishes the legal provenance, copyright licensing conditions, attribution requirements, and data risk assessments for all external datasets, APIs, and regulatory publications utilized by YumSure.

---

## 1. Statutory & Regulatory Documentation

### 1.1 Food Safety and Standards Authority of India (FSSAI)
- **Content**: Food Safety and Standards Act (2006), Food Safety and Standards (Labelling and Display) Regulations (2020), Food Safety and Standards (Advertising and Claims) Regulations (2018), along with gazetted amendments.
- **License / Legal Status**: Official Government of India Gazette Notifications and public statutory regulations. Published under the Gazette of India under the authority of the Central Government.
- **Attribution & Usage**: Unrestricted public access for regulatory adherence and citizen information. YumSure cites the exact gazette notification and schedule numbers.
- **Official URLs**:
  - `https://www.fssai.gov.in/food-law/regulations`
  - `https://www.fssai.gov.in/food-law/regulations/amendments/labelling-display`
  - `https://fssai.gov.in/food-law/regulations/amendments/advertising-claims`

### 1.2 ICMR - National Institute of Nutrition (NIN)
- **Content**: "Nutrient Requirements for Indians" and "Recommended Dietary Allowances (RDA) for Indians" (2020 Report of the Expert Group).
- **License / Legal Status**: Public health guidelines issued by the Indian Council of Medical Research (Ministry of Health and Family Welfare, Government of India).
- **Usage**: Used strictly as defensible quantitative reference baselines for calculating percentage daily values.

---

## 2. External Product Catalog: Open Food Facts

### 2.1 Licensing Overview
- **Database License**: **Open Database License (ODbL) v1.0** (Open Data Commons).
- **Individual Contents License**: **Database Contents License (DbCL) v1.0**; individual images and textual descriptions contributed under **Creative Commons Attribution-ShareAlike 3.0 (CC-BY-SA 3.0)** or newer.
- **License Documentation**: `https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/license-be-on-the-legal-side/`

### 2.2 Legal Obligations Under ODbL
1. **Attribution**: YumSure must visibly display attribution to Open Food Facts in the mobile application UI and documentation:
   > *"Product data sourced from Open Food Facts, licensed under the Open Database License (ODbL)."*
2. **Share-Alike (SA)**: If YumSure creates an enriched or modified derivative database and distributes that database publicly, the modified database must be made available under the ODbL.
3. **Keep Open**: If YumSure redistributes the database with technical DRM restrictions, an unrestricted version must be offered alongside it.

### 2.3 Technical Access Rules & Good Citizenship
- **API Version**: Open Food Facts API v3 (`https://world.openfoodfacts.org/api/v3/product/{barcode}.json`).
- **User-Agent Header**: Fulfills the strict OFF specification:
  ```http
  User-Agent: YumSureApp/1.0.0 (Android; contact: developer@yumsure.in)
  ```
- **Rate-Limiting & Caching**:
  - Responses are cached in PostgreSQL.
  - Redundant lookups for the same barcode bypass the OFF API completely.
  - Network timeouts are set strictly to 5.0 seconds with exponential backoff on HTTP 429/503.

---

## 3. Kaggle Datasets & Secondary Data Sources

### 3.1 Licensing Audit Framework
Before any supplementary Kaggle dataset is introduced into YumSure, it must undergo a mandatory 4-point verification check:

```mermaid
flowchart TD
    Start[Proposed Kaggle Dataset] --> Check1{Is License Documented?}
    Check1 -- No --> Reject[REJECT: Ambiguous or Unspecified License]
    Check1 -- Yes --> Check2{Is License Commercial Friendly?\nCC0, CC-BY 4.0, ODbL}
    Check2 -- No (e.g. CC-BY-NC) --> RejectNonComm[REJECT: Non-Commercial terms clash with production deployment]
    Check2 -- Yes --> Check3{Is Data Scraped from Private E-Commerce?\ne.g. Blinkit, Zepto, BigBasket}
    Check3 -- Yes --> RejectToS[REJECT: Scraped data violates third-party Terms of Service]
    Check3 -- No --> Check4{Does Schema Align with FSSAI Nutrients?}
    Check4 -- No --> Transform[Requires Normalization Pipeline]
    Check4 -- Yes --> Approve[APPROVED: Import with Provenance Tag KAGGLE_AUDITED]
```

### 3.2 Approved Dataset Inventory

| Dataset Identifier | Creator / Source | License | Permitted Usage | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Indian Food Packaged Nutrition** | Verified Public Open Data | CC0 1.0 Universal / Public Domain | Unrestricted commercial & educational reuse | Verified Compatible |
| **FSSAI Standard Additives Codex** | Government Gazette Extracts | Public Domain Government Data | Statutory reference mapping | Verified Compatible |
| *Scraped E-Commerce Sets* | Various Kaggle Uploaders | Unknown / ToS Violations | Strictly prohibited from YumSure repository | REJECTED |

---

## 4. AI Provider APIs (xAI Grok & NVIDIA NIM)

- **xAI API Terms**: Commercial API terms (`https://docs.x.ai/docs`). YumSure backend acts as the sole API key custodian. Keys are never transmitted to client devices.
- **NVIDIA Build NIM Terms**: Enterprise developer API agreement (`https://build.nvidia.com/`).
- **Data Privacy & Transmission**:
  - Only anonymized product nutrient tokens and calculated claim tags are transmitted to LLM completion endpoints.
  - No user personal data, IP addresses, or device identifiers are ever forwarded to AI providers.

---

## 5. Third-Party Application Reference Boundary (TruthIn)

- **Clean-Room Analysis Only**: YumSure benchmarks user experience patterns against Indian nutrition apps like TruthIn purely via public, visible mobile workflows.
- **Absolute Boundaries**:
  - No reverse engineering of private TruthIn API endpoints.
  - No extraction of authentication tokens or headers.
  - Zero code borrowing or decompilation of proprietary binaries.
  - Zero runtime dependencies on third-party infrastructure.

---

## 6. Category Photography Assets (Public Domain & Unsplash License)

To maintain authentic culinary representation matching the design specifications, category tiles utilize verified, single-subject studio food photography:

| Category | Local Asset Path | Subject & Studio Setup | Source / Photographer | License |
| :--- | :--- | :--- | :--- | :--- |
| **Snacks** | `assets/images/categories/snacks.webp` | Golden crispy potato chips, close-up food photography with warm golden tones | [Evan-Amos](https://commons.wikimedia.org/wiki/File:Potato-Chips.jpg) | Public Domain (CC0) |
| **Beverages** | `assets/images/categories/beverages.webp` | Clear glass with dark amber cola being poured over ice cubes against light background | [Slashio Photography](https://images.unsplash.com/photo-1552879574-e1a9ae64c38a) | Unsplash License |
| **Biscuits** | `assets/images/categories/biscuits.webp` | Round golden-brown chocolate chip cookies arranged on warm studio surface | [Evan-Amos](https://commons.wikimedia.org/wiki/File:Choc-Chip-Cookie.png) | Public Domain (CC0) |
| **Dairy** | `assets/images/categories/dairy.webp` | White milk streaming into a clear glass jar against a minimalist pale background | [NordWood Themes](https://images.unsplash.com/photo-1528750997573-59b89d56f4f7) | Unsplash License |

---

## 7. Bundled Typography: Manrope (SIL Open Font License 1.1)

- **Font Family**: Manrope
- **Designer / Custodian**: Mikhail Sharanda, Mirko Velimirovic
- **License**: **SIL Open Font License (OFL) Version 1.1**
- **Repository**: `https://github.com/google/fonts/tree/main/ofl/manrope`
- **Permitted Uses**: Free of charge to use, study, copy, merge, embed, and redistribute with software.
- **Bundled Files**:
  - `assets/fonts/manrope/Manrope-Regular.ttf` (Weight 400)
  - `assets/fonts/manrope/Manrope-Medium.ttf` (Weight 500)
  - `assets/fonts/manrope/Manrope-SemiBold.ttf` (Weight 600)
  - `assets/fonts/manrope/Manrope-Bold.ttf` (Weight 700)
  - `assets/fonts/manrope/Manrope-ExtraBold.ttf` (Weight 800)

---

## 8. Brand Identity & Vector Logo Provenance

The YumSure brand assets were reconstructed as an original, standalone vector identity matching the visual character of the approved UI references:

| Property | Specification |
| :--- | :--- |
| **Wordmark Text** | `YumSure` (Capital Y and S, dark near-black `#16141A`) |
| **Typography Source** | **Manrope ExtraBold (Weight 800)** from Google Fonts (`https://fonts.google.com/specimen/Manrope`) |
| **Typography Licence** | **SIL Open Font License (OFL) Version 1.1** (`https://openfontlicense.org/`) |
| **Vector Geometry** | Outlined Bezier `<path>` glyphs generated directly from font metrics via `fontTools`, completely independent of device-installed fonts |
| **Smile Artwork** | Original custom Bezier arc in YumSure signature orange (`#FE873E`), stroke width 2.3 with smooth rounded caps (`stroke-linecap="round"`), integrated directly below the wordmark under the `m` and `S` baseline (relative X range: 0.49 to 0.64) |
| **Asset Files** | `assets/images/yumsure_logo.svg` (primary scalable vector asset) |
| **Copyright Compliance** | Zero third-party logos copied; zero unverified internet assets; 100% original typographic and vector artwork |

---

## 9. Background & Illustration Artwork Ledger

All decorative backgrounds and interface illustrations are original assets created specifically for YumSure to eliminate third-party dependencies and real-time GPU blur penalties:

| Asset Name | Local File Path | Format & Dimensions | Authorship & License |
| :--- | :--- | :--- | :--- |
| **Home Aurora Background (WebP)** | `assets/backgrounds/home_bg.webp` | WebP (780 × 1600 px, 16.2 KB) | Original artwork for YumSure (MIT License) |
| **Barcode Hero Illustration** | `assets/illustrations/barcode_bracket.svg` | SVG (60 × 40 px, 0.9 KB) | Original artwork for YumSure (MIT License) — 4 separate corner brackets with 6 vertical barcode stripes |




