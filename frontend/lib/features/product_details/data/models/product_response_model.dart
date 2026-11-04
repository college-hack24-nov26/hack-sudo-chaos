class ProductDetailsResponse {
  final ProductIdentity product;
  final NutritionalInterpretation? nutritionalInterpretation;
  final RegulatoryClaimsValidation? regulatoryClaimsValidation;
  final IngredientAnalysis? ingredientAnalysis;
  final List<KeyFindingItem> keyFindings;
  final AiExplanation? aiExplanation;

  const ProductDetailsResponse({
    required this.product,
    this.nutritionalInterpretation,
    this.regulatoryClaimsValidation,
    this.ingredientAnalysis,
    this.keyFindings = const [],
    this.aiExplanation,
  });

  // =========================================================================
  // Completeness & Incomplete Data Evaluation
  // =========================================================================

  bool get isProductDetailsAvailable {
    return product.productName.trim().isNotEmpty &&
        (product.brandName != null ||
            product.foodCategory != null ||
            product.packageSize != null ||
            product.hasServingInfo);
  }

  bool _isNutrientAvailable(List<String> codes) {
    final list = nutritionalInterpretation?.nutrients;
    if (list == null || list.isEmpty) return false;
    for (final item in list) {
      final code = item.nutrientCode.toLowerCase();
      final name = item.displayName.toLowerCase();
      if (codes.any((c) => code == c || name.contains(c))) {
        if (item.status == 'EXPLICITLY_ZERO') return true;
        if (item.status == 'NOT_DECLARED' || item.status == 'UNKNOWN') return false;
        return item.valuePer100g != null || item.valuePerServing != null;
      }
    }
    return false;
  }

  bool _hasNutrientEntry(List<String> codes) {
    final list = nutritionalInterpretation?.nutrients;
    if (list == null || list.isEmpty) return false;
    for (final item in list) {
      final code = item.nutrientCode.toLowerCase();
      final name = item.displayName.toLowerCase();
      if (codes.any((c) => code == c || name.contains(c))) {
        return true;
      }
    }
    return false;
  }

  bool get isEnergyAvailable => _isNutrientAvailable(const ['energy', 'calories', 'energy_kcal']);
  bool get isTotalFatAvailable => _isNutrientAvailable(const ['total_fat', 'fat']);
  bool get isSodiumAvailable => _isNutrientAvailable(const ['sodium', 'salt']);
  bool get isProteinAvailable => _isNutrientAvailable(const ['protein']);
  bool get isAddedSugarAvailable => _isNutrientAvailable(const ['added_sugars', 'added_sugar', 'sugars']);
  bool get isCarbohydratesAvailable => _isNutrientAvailable(const ['carbohydrates', 'carbohydrate', 'carbs']);
  bool get isIngredientsDetailedAvailable {
    final ing = ingredientAnalysis;
    if (ing == null) return false;
    if (ing.ingredientsSummary != null && ing.ingredientsSummary!.trim().isNotEmpty) return true;
    if (ing.categories.isNotEmpty) return true;
    if (ing.totalIngredientsCount > 0) return true;
    return false;
  }

  List<ProductDataFieldStatus> get completenessEvaluation {
    return [
      ProductDataFieldStatus(
        label: 'Product details',
        isAvailable: isProductDetailsAvailable,
      ),
      ProductDataFieldStatus(
        label: 'Energy (Calories)',
        isAvailable: isEnergyAvailable,
      ),
      ProductDataFieldStatus(
        label: 'Total Fat',
        isAvailable: isTotalFatAvailable,
      ),
      ProductDataFieldStatus(
        label: 'Sodium',
        isAvailable: isSodiumAvailable,
      ),
      if (isCarbohydratesAvailable)
        const ProductDataFieldStatus(
          label: 'Carbohydrates',
          isAvailable: true,
        ),
      ProductDataFieldStatus(
        label: 'Protein',
        isAvailable: isProteinAvailable,
      ),
      ProductDataFieldStatus(
        label: 'Added Sugar',
        isAvailable: isAddedSugarAvailable,
      ),
      if (!isCarbohydratesAvailable && _hasNutrientEntry(const ['carbohydrates', 'carbohydrate', 'carbs']))
        const ProductDataFieldStatus(
          label: 'Carbohydrates',
          isAvailable: false,
        ),
      ProductDataFieldStatus(
        label: 'Ingredients (Detailed)',
        isAvailable: isIngredientsDetailedAvailable,
      ),
    ];
  }

  List<String> get availableFields =>
      completenessEvaluation.where((f) => f.isAvailable).map((f) => f.label).toList();

  List<String> get missingFields =>
      completenessEvaluation.where((f) => !f.isAvailable).map((f) => f.label).toList();

  bool get hasIncompleteData => missingFields.isNotEmpty;

  static ProductDetailsResponse get demoIncompleteLays => const ProductDetailsResponse(
        product: ProductIdentity(
          barcode: '8901491101837',
          productName: "Lay's Classic",
          brandName: "Lay's",
          foodCategory: 'Potato Chips',
          packageSize: '100 g',
          foodForm: 'solid',
        ),
        nutritionalInterpretation: NutritionalInterpretation(
          nutrients: [
            NutrientItem(
              nutrientCode: 'energy',
              displayName: 'Energy',
              valuePer100g: 544.0,
              unit: 'kcal',
              status: 'PRESENT',
            ),
            NutrientItem(
              nutrientCode: 'total_fat',
              displayName: 'Total Fat',
              valuePer100g: 34.0,
              unit: 'g',
              status: 'PRESENT',
            ),
            NutrientItem(
              nutrientCode: 'sodium',
              displayName: 'Sodium',
              valuePer100g: 550.0,
              unit: 'mg',
              status: 'PRESENT',
            ),
            NutrientItem(
              nutrientCode: 'protein',
              displayName: 'Protein',
              status: 'NOT_DECLARED',
              unit: 'g',
            ),
            NutrientItem(
              nutrientCode: 'added_sugars',
              displayName: 'Added Sugar',
              status: 'NOT_DECLARED',
              unit: 'g',
            ),
          ],
        ),
      );

  factory ProductDetailsResponse.fromJson(Map<String, dynamic> json) {
    return ProductDetailsResponse(
      product: ProductIdentity.fromJson(json['product'] as Map<String, dynamic>? ?? {}),
      nutritionalInterpretation: json['nutritional_interpretation'] != null
          ? NutritionalInterpretation.fromJson(json['nutritional_interpretation'] as Map<String, dynamic>)
          : null,
      regulatoryClaimsValidation: json['regulatory_claims_validation'] != null
          ? RegulatoryClaimsValidation.fromJson(json['regulatory_claims_validation'] as Map<String, dynamic>)
          : null,
      ingredientAnalysis: json['ingredient_analysis'] != null
          ? IngredientAnalysis.fromJson(json['ingredient_analysis'] as Map<String, dynamic>)
          : null,
      keyFindings: (json['key_findings'] as List<dynamic>?)
              ?.map((e) => KeyFindingItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      aiExplanation: json['ai_explanation'] != null
          ? AiExplanation.fromJson(json['ai_explanation'] as Map<String, dynamic>)
          : null,
    );
  }
}

class ProductIdentity {
  final String barcode;
  final String productName;
  final String? brandName;
  final String? packageSize;
  final double? servingSizeValue;
  final String? servingSizeUnit;
  final String foodForm; // 'solid' or 'liquid'
  final String? foodCategory;
  final bool isVerified;
  final bool? isVeg; // true: veg, false: non-veg, null: unknown
  final String? imageUrl;
  final String? sourceProvenance;
  final String? sourceRetrievalDate;

  const ProductIdentity({
    required this.barcode,
    required this.productName,
    this.brandName,
    this.packageSize,
    this.servingSizeValue,
    this.servingSizeUnit,
    this.foodForm = 'solid',
    this.foodCategory,
    this.isVerified = false,
    this.isVeg,
    this.imageUrl,
    this.sourceProvenance,
    this.sourceRetrievalDate,
  });

  bool get hasServingInfo => servingSizeValue != null && servingSizeValue! > 0;

  String get formattedServingSize {
    if (!hasServingInfo) return '';
    final numVal = servingSizeValue!.toStringAsFixed(servingSizeValue!.truncateToDouble() == servingSizeValue! ? 0 : 1);
    return '$numVal ${servingSizeUnit ?? (foodForm == 'liquid' ? 'ml' : 'g')}';
  }

  factory ProductIdentity.fromJson(Map<String, dynamic> json) {
    return ProductIdentity(
      barcode: json['barcode']?.toString() ?? '',
      productName: json['product_name']?.toString() ?? 'Unknown Product',
      brandName: json['brand_name']?.toString(),
      packageSize: json['package_size']?.toString(),
      servingSizeValue: (json['serving_size_value'] as num?)?.toDouble(),
      servingSizeUnit: json['serving_size_unit']?.toString(),
      foodForm: json['food_form']?.toString() ?? 'solid',
      foodCategory: json['food_category']?.toString(),
      isVerified: json['is_verified'] as bool? ?? false,
      isVeg: json['is_veg'] as bool?,
      imageUrl: json['image_url']?.toString(),
      sourceProvenance: json['source_provenance']?.toString(),
      sourceRetrievalDate: json['source_retrieval_date']?.toString(),
    );
  }
}

class NutritionalInterpretation {
  final String basis;
  final String referenceStandard;
  final List<NutrientItem> nutrients;
  final double? servingSizeValue;
  final String servingSizeUnit;
  final String dataQuality;
  final List<String> dataInconsistencies;

  const NutritionalInterpretation({
    this.basis = 'per_100g',
    this.referenceStandard = 'ICMR-NIN 2020 RDA',
    this.nutrients = const [],
    this.servingSizeValue,
    this.servingSizeUnit = 'g',
    this.dataQuality = 'VERIFIED',
    this.dataInconsistencies = const [],
  });

  factory NutritionalInterpretation.fromJson(Map<String, dynamic> json) {
    return NutritionalInterpretation(
      basis: json['basis']?.toString() ?? 'per_100g',
      referenceStandard: json['reference_standard']?.toString() ?? 'ICMR-NIN 2020 RDA',
      servingSizeValue: (json['serving_size_value'] as num?)?.toDouble(),
      servingSizeUnit: json['serving_size_unit']?.toString() ?? 'g',
      dataQuality: json['data_quality']?.toString() ?? 'VERIFIED',
      dataInconsistencies: (json['data_inconsistencies'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          const [],
      nutrients: (json['nutrients'] as List<dynamic>?)
              ?.map((e) => NutrientItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

class NutrientItem {
  final String nutrientCode;
  final String displayName;
  final double? valuePer100g;
  final double? valuePerServing;
  final String unit;
  final double? rdaPercentage;
  final String? classification; // 'Low', 'Moderate', 'High', 'Not classifiable', 'Insufficient data'
  final String? concernLevel; // 'POSITIVE', 'NEUTRAL', 'CONCERN'
  final String status; // 'PRESENT', 'EXPLICITLY_ZERO', 'NOT_DECLARED', 'UNKNOWN'
  final String? explanation;
  final double? lowThresholdMax;
  final double? moderateThresholdMax;
  final double? highThresholdMin;

  const NutrientItem({
    required this.nutrientCode,
    required this.displayName,
    this.valuePer100g,
    this.valuePerServing,
    required this.unit,
    this.rdaPercentage,
    this.classification,
    this.concernLevel,
    this.status = 'PRESENT',
    this.explanation,
    this.lowThresholdMax,
    this.moderateThresholdMax,
    this.highThresholdMin,
  });

  bool get hasThresholdScale =>
      lowThresholdMax != null && moderateThresholdMax != null && highThresholdMin != null;

  factory NutrientItem.fromJson(Map<String, dynamic> json) {
    return NutrientItem(
      nutrientCode: json['nutrient_code']?.toString() ?? '',
      displayName: json['display_name']?.toString() ?? '',
      valuePer100g: (json['value_per_100g'] as num?)?.toDouble(),
      valuePerServing: (json['value_per_serving'] as num?)?.toDouble(),
      unit: json['unit']?.toString() ?? 'g',
      rdaPercentage: (json['rda_percentage'] as num?)?.toDouble(),
      classification: json['classification']?.toString(),
      concernLevel: json['concern_level']?.toString(),
      status: json['status']?.toString() ?? 'PRESENT',
      explanation: json['explanation']?.toString(),
      lowThresholdMax: (json['low_threshold_max'] as num?)?.toDouble(),
      moderateThresholdMax: (json['moderate_threshold_max'] as num?)?.toDouble(),
      highThresholdMin: (json['high_threshold_min'] as num?)?.toDouble(),
    );
  }
}

class RegulatoryClaimsValidation {
  final String applicableRegulation;
  final bool? isFssaiCompliant;
  final List<RegulatoryClaimItem> claims;

  const RegulatoryClaimsValidation({
    required this.applicableRegulation,
    this.isFssaiCompliant,
    this.claims = const [],
  });

  factory RegulatoryClaimsValidation.fromJson(Map<String, dynamic> json) {
    return RegulatoryClaimsValidation(
      applicableRegulation: json['applicable_regulation']?.toString() ??
          'FSSAI (Advertising and Claims) Regulations, 2018',
      isFssaiCompliant: json['is_fssai_compliant'] as bool?,
      claims: (json['claims'] as List<dynamic>?)
              ?.map((e) => RegulatoryClaimItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

class RegulatoryClaimItem {
  final String claimCode;
  final String claimName;
  final String status; // 'COMPLIANT', 'NOT_COMPLIANT', 'INSUFFICIENT_DATA', 'NOT_EVALUATED'
  final double? actualValue;
  final double? requiredThreshold;
  final String? unit;
  final String? regulatoryReference;
  final String? explanation;

  const RegulatoryClaimItem({
    required this.claimCode,
    required this.claimName,
    required this.status,
    this.actualValue,
    this.requiredThreshold,
    this.unit,
    this.regulatoryReference,
    this.explanation,
  });

  factory RegulatoryClaimItem.fromJson(Map<String, dynamic> json) {
    return RegulatoryClaimItem(
      claimCode: json['claim_code']?.toString() ?? '',
      claimName: json['claim_name']?.toString() ?? '',
      status: json['status']?.toString() ?? 'NOT_EVALUATED',
      actualValue: (json['actual_value'] as num?)?.toDouble(),
      requiredThreshold: (json['required_threshold'] as num?)?.toDouble(),
      unit: json['unit']?.toString(),
      regulatoryReference: json['regulatory_reference']?.toString(),
      explanation: json['explanation']?.toString(),
    );
  }
}

class IngredientAnalysis {
  final int totalIngredientsCount;
  final String? ingredientsSummary;
  final List<String> declaredAllergens;
  final List<String> mayContainAllergens;
  final List<IngredientCategory> categories;

  const IngredientAnalysis({
    this.totalIngredientsCount = 0,
    this.ingredientsSummary,
    this.declaredAllergens = const [],
    this.mayContainAllergens = const [],
    this.categories = const [],
  });

  factory IngredientAnalysis.fromJson(Map<String, dynamic> json) {
    return IngredientAnalysis(
      totalIngredientsCount: json['total_ingredients_count'] as int? ?? 0,
      ingredientsSummary: json['ingredients_summary']?.toString(),
      declaredAllergens: (json['declared_allergens'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      mayContainAllergens: (json['may_contain_allergens'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
      categories: (json['categories'] as List<dynamic>?)
              ?.map((e) => IngredientCategory.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }
}

class IngredientCategory {
  final String category;
  final String categoryName;
  final int count;
  final List<String> items;

  const IngredientCategory({
    required this.category,
    required this.categoryName,
    this.count = 0,
    this.items = const [],
  });

  factory IngredientCategory.fromJson(Map<String, dynamic> json) {
    return IngredientCategory(
      category: json['category']?.toString() ?? '',
      categoryName: json['category_name']?.toString() ?? json['category']?.toString() ?? '',
      count: json['count'] as int? ?? 0,
      items: (json['items'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
    );
  }
}

class KeyFindingItem {
  final String nutrientCode;
  final String title;
  final String valueText;
  final String severity; // 'HIGH', 'MODERATE', 'POSITIVE'
  final String? explanation;

  const KeyFindingItem({
    required this.nutrientCode,
    required this.title,
    required this.valueText,
    required this.severity,
    this.explanation,
  });

  factory KeyFindingItem.fromJson(Map<String, dynamic> json) {
    return KeyFindingItem(
      nutrientCode: json['nutrient_code']?.toString() ?? '',
      title: json['title']?.toString() ?? '',
      valueText: json['value_text']?.toString() ?? '',
      severity: json['severity']?.toString() ?? 'MODERATE',
      explanation: json['explanation']?.toString(),
    );
  }
}

class AiExplanation {
  final String? provider;
  final bool isFallback;
  final String text;

  const AiExplanation({
    this.provider,
    this.isFallback = false,
    required this.text,
  });

  factory AiExplanation.fromJson(Map<String, dynamic> json) {
    return AiExplanation(
      provider: json['provider']?.toString(),
      isFallback: json['is_fallback'] as bool? ?? false,
      text: json['text']?.toString() ?? '',
    );
  }
}



class ProductDataFieldStatus {
  final String label;
  final bool isAvailable;

  const ProductDataFieldStatus({
    required this.label,
    required this.isAvailable,
  });
}
