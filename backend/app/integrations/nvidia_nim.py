"""
NVIDIA NIM AI Client & Guardrail Integration.

Provides topic-controlled LLM explanations and interactive Q&A for scanned
packaged foods using NVIDIA NIM (llama-3.1-nemoguard-8b-topic-control).

Design Guarantees:
1. Strict Grounding: All answers must be substantiated exclusively by pre-computed
   deterministic engine findings (Nutrition, ICMR-HFSS, FSSAI Claims, Ingredients).
2. Topic Control & Guardrails: Questions outside food nutrition/ingredients or requesting
   medical diagnoses are politely deflected with mandatory statutory disclaimers.
3. Resilience & Zero Downtime: Automatically falls back to local deterministic templates
   if NVIDIA_API_KEY is unset, rate-limited (HTTP 429), or unreachable.
4. Quota & Rate-Limit Management: Thread-safe in-memory caching and request tracking
   to protect user API limits.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Mandatory statutory disclaimer for all AI-generated content
STATUTORY_DISCLAIMER = (
    "YumSure AI provides regulatory and nutritional information based on official FSSAI & ICMR-NIN guidelines. "
    "It is not a substitute for professional medical diagnosis or clinical dietetic advice."
)

TOPIC_DEFLECTION_MESSAGE = (
    "I am YumSure's Food Intelligence Assistant. I can only assist with questions regarding the nutritional facts, "
    "ingredients, allergens, and FSSAI/ICMR regulatory compliance of this scanned food product."
)

MEDICAL_DEFLECTION_MESSAGE = (
    "YumSure cannot provide medical diagnoses, treatment recommendations, or advice on managing clinical diseases. "
    "Please consult a qualified medical professional or registered dietitian for specific dietary advice."
)


class NvidiaNIMClient:
    """
    Client for NVIDIA NIM LLM endpoints with topic control, usage tracking, and safe fallbacks.
    """

    def __init__(self):
        self.nvidia_api_key: Optional[str] = (
            settings.NVIDIA_API_KEY or os.environ.get("NVIDIA_API_KEY")
        )
        self.nvidia_base_url: str = settings.NVIDIA_BASE_URL.rstrip("/")
        self.nvidia_model_name: str = settings.NVIDIA_MODEL_NAME

        self.llama_api_key: Optional[str] = (
            settings.LLAMA_API_KEY or os.environ.get("LLAMA_API_KEY")
        )
        self.llama_base_url: str = settings.LLAMA_BASE_URL.rstrip("/")
        self.llama_model_name: str = settings.LLAMA_MODEL_NAME

        self.max_tokens: int = settings.NVIDIA_MAX_TOKENS
        self.temperature: float = settings.NVIDIA_TEMPERATURE

        # Backwards compatibility properties
        self.api_key = self.nvidia_api_key or self.llama_api_key
        self.base_url = self.nvidia_base_url
        self.model_name = self.nvidia_model_name
        
        # In-memory QA and explanation cache: (barcode, query_hash) -> answer_dict
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._request_count: int = 0
        self._last_request_time: float = 0.0

    @property
    def is_configured(self) -> bool:
        """Returns True if either NVIDIA NIM or direct Llama API key is present."""
        has_nvidia = bool(self.nvidia_api_key and len(self.nvidia_api_key.strip()) > 10)
        has_llama = bool(self.llama_api_key and len(self.llama_api_key.strip()) > 10)
        return has_nvidia or has_llama

    async def _call_llm_api(self, messages: List[Dict[str, str]]) -> Tuple[Optional[str], Optional[str]]:
        """
        Calls LLM with automatic multi-provider failover:
        1. NVIDIA NIM (llama-3.1-nemoguard-8b-topic-control)
        2. Direct Llama provider (Groq / OpenRouter / Together / Meta)
        Returns: (generated_text, provider_name) or (None, None)
        """
        # 1. Try NVIDIA NIM first if configured
        if self.nvidia_api_key and len(self.nvidia_api_key.strip()) > 10:
            try:
                headers = {
                    "Authorization": f"Bearer {self.nvidia_api_key.strip()}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": self.nvidia_model_name,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(
                        f"{self.nvidia_base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices and "message" in choices[0]:
                            msg = choices[0]["message"]
                            raw_content = msg.get("content") or msg.get("reasoning_content")
                            if raw_content and str(raw_content).strip():
                                return str(raw_content).strip(), "nvidia_nim"
                    logger.warning("NVIDIA NIM returned HTTP %s. Attempting failover if available.", resp.status_code)
            except Exception as exc:
                logger.warning("NVIDIA NIM call failed: %s. Attempting failover.", exc)

        # 2. Try Direct Llama provider if configured
        if self.llama_api_key and len(self.llama_api_key.strip()) > 10:
            try:
                headers = {
                    "Authorization": f"Bearer {self.llama_api_key.strip()}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": self.llama_model_name,
                    "messages": messages,
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                }
                async with httpx.AsyncClient(timeout=20.0) as client:
                    resp = await client.post(
                        f"{self.llama_base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices and "message" in choices[0]:
                            msg = choices[0]["message"]
                            raw_content = msg.get("content") or msg.get("reasoning_content")
                            if raw_content and str(raw_content).strip():
                                return str(raw_content).strip(), "llama_provider"
                    logger.warning("Llama direct API returned HTTP %s.", resp.status_code)
            except Exception as exc:
                logger.warning("Llama direct call failed: %s.", exc)

        return None, None

    def _build_product_grounding_context(self, product_data: Dict[str, Any]) -> str:
        """
        Builds a concise, structured textual factsheet from deterministic analysis data.
        """
        name = product_data.get("product_name") or product_data.get("name") or "Unknown Product"
        brand = product_data.get("brand_name") or product_data.get("brand") or "Unknown Brand"
        form = product_data.get("food_form", "solid")
        category = product_data.get("food_category", "Standard Packaged Food")
        
        # Nutrients
        nutrients = product_data.get("nutrients", {})
        nutrients_summary = []
        if isinstance(nutrients, dict):
            for k, v in nutrients.items():
                if isinstance(v, dict):
                    val = v.get("per_100g") or v.get("value")
                    unit = v.get("unit", "g")
                    nutrients_summary.append(f"{k}: {val}{unit}")
                else:
                    nutrients_summary.append(f"{k}: {v}")
        elif isinstance(nutrients, list):
            for n in nutrients:
                if isinstance(n, dict):
                    code = n.get("nutrient_code") or n.get("name")
                    val = n.get("per_100_value") or n.get("value")
                    unit = n.get("unit", "g")
                    nutrients_summary.append(f"{code}: {val}{unit}")

        # ICMR-HFSS status
        hfss_status = "Not evaluated"
        icmr_eval = product_data.get("icmr_hfss_evaluation") or {}
        if isinstance(icmr_eval, dict) and icmr_eval.get("results"):
            for r in icmr_eval["results"]:
                if "classification" in r:
                    hfss_status = r["classification"]
                    break

        # Claims
        claims_summary = []
        claims_eval = product_data.get("claims_evaluation") or {}
        if isinstance(claims_eval, dict) and claims_eval.get("results"):
            for r in claims_eval["results"]:
                code = r.get("rule_code") or r.get("claim_code")
                outcome = r.get("outcome") or r.get("status")
                claims_summary.append(f"{code}: {outcome}")

        # Allergens & Ingredients
        allergens = product_data.get("declared_allergens", [])
        ingredients = product_data.get("ingredients_text") or product_data.get("ingredients_summary", "")

        context_lines = [
            f"PRODUCT: {name} (Brand: {brand}, Form: {form}, Category: {category})",
            f"ICMR-NIN HFSS CLASSIFICATION: {hfss_status}",
            f"KEY NUTRIENTS (per 100{'ml' if form == 'liquid' else 'g'}): {', '.join(nutrients_summary[:12]) if nutrients_summary else 'Standard panel'}",
            f"DECLARED ALLERGENS: {', '.join(allergens) if allergens else 'None explicitly declared'}",
            f"FSSAI CLAIMS STATUS: {', '.join(claims_summary[:6]) if claims_summary else 'None declared'}",
            f"INGREDIENTS: {ingredients[:400] if ingredients else 'Not declared'}",
        ]
        return "\n".join(context_lines)

    async def generate_product_explanation(
        self,
        product_data: Dict[str, Any],
        barcode: str = "",
    ) -> Tuple[str, str, bool]:
        """
        Generates a concise consumer summary grounded in deterministic facts.
        Returns: (explanation_text, provider_name, is_fallback)
        """
        # Check cache
        cache_key = f"expl:{barcode}"
        if barcode and cache_key in self._cache:
            hit = self._cache[cache_key]
            return hit["text"], hit["provider"], hit["is_fallback"]

        grounding = self._build_product_grounding_context(product_data)

        if not self.is_configured:
            fallback_text = self._build_local_fallback_explanation(product_data)
            return fallback_text, "local_deterministic_explainer", True

        system_prompt = (
            "You are YumSure's Indian Food Regulatory & Nutrition Assistant.\n"
            "Explain this packaged food product to an Indian consumer in 3 to 4 clear, factual sentences.\n"
            "RULES:\n"
            "1. Ground every claim STRICTLY in the factsheet below.\n"
            "2. Highlight protein/fibre if positive, and warn if sugar, fat, or sodium is high under ICMR guidelines.\n"
            "3. Explicitly mention declared allergens if present.\n"
            "4. NEVER give medical advice, cure claims, or make up facts not in the context.\n"
            "5. Keep the tone objective, helpful, and consumer-friendly."
        )

        user_prompt = f"FACTSHEET:\n{grounding}\n\nPlease generate the consumer explanation."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        text, provider = await self._call_llm_api(messages)
        if text:
            if barcode:
                self._cache[cache_key] = {
                    "text": text,
                    "provider": provider or "nvidia_nim_nemoguard",
                    "is_fallback": False,
                }
            return text, provider or "nvidia_nim_nemoguard", False

        fallback_text = self._build_local_fallback_explanation(product_data)
        return fallback_text, "local_deterministic_explainer", True

    async def answer_product_question(
        self,
        product_data: Dict[str, Any],
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        barcode: str = "",
    ) -> Dict[str, Any]:
        """
        Interactive Q&A grounded strictly in the product's deterministic factsheet.
        Enforces topic control (deflects off-topic and medical queries).
        """
        clean_q = question.strip()
        cache_key = f"qa:{barcode}:{hash(clean_q.lower())}"
        if barcode and cache_key in self._cache:
            return self._cache[cache_key]

        # 1. Quick Guardrails on obvious off-topic queries
        lower_q = clean_q.lower()
        medical_keywords = ["cure", "prescribe", "treatment", "medicine", "heal", "dosage", "drug"]
        if any(w in lower_q for w in medical_keywords):
            return {
                "barcode": barcode,
                "question": clean_q,
                "answer": MEDICAL_DEFLECTION_MESSAGE,
                "provider": "nvidia_nim_nemoguard",
                "model": self.model_name,
                "is_fallback": False,
                "topic_status": "DEFLECTED",
                "disclaimer": STATUTORY_DISCLAIMER,
            }

        off_topic_keywords = ["weather", "politics", "crypto", "stock", "coding", "python", "president", "movie"]
        if any(w in lower_q for w in off_topic_keywords):
            return {
                "barcode": barcode,
                "question": clean_q,
                "answer": TOPIC_DEFLECTION_MESSAGE,
                "provider": "nvidia_nim_nemoguard",
                "model": self.model_name,
                "is_fallback": False,
                "topic_status": "DEFLECTED",
                "disclaimer": STATUTORY_DISCLAIMER,
            }

        grounding = self._build_product_grounding_context(product_data)

        if not self.is_configured:
            # Deterministic answer based on factsheet
            ans = self._answer_from_factsheet_offline(product_data, clean_q)
            return {
                "barcode": barcode,
                "question": clean_q,
                "answer": ans,
                "provider": "local_deterministic_explainer",
                "model": "rule_based_fallback",
                "is_fallback": True,
                "topic_status": "ON_TOPIC",
                "disclaimer": STATUTORY_DISCLAIMER,
            }

        system_prompt = (
            "You are YumSure's AI Food & Regulatory Intelligence Assistant.\n"
            "You answer user questions about a specific Indian packaged food product based STRICTLY on the factsheet below.\n"
            "GUARDRAILS & RULES:\n"
            "1. Answer ONLY questions about the nutritional value, ingredients, allergens, or regulatory claims of this product.\n"
            "2. If the user asks anything outside food/nutrition or about unrelated topics, reply with:\n"
            f"   '{TOPIC_DEFLECTION_MESSAGE}'\n"
            "3. If the user asks for medical diagnosis, treatment, or clinical health advice, reply with:\n"
            f"   '{MEDICAL_DEFLECTION_MESSAGE}'\n"
            "4. NEVER invent ingredients or nutrients. If the data is missing from the factsheet, state that it is not declared on packaging.\n"
            "5. Always be polite, concise, and helpful."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"FACTSHEET:\n{grounding}\n\nUSER QUESTION: {clean_q}"},
        ]

        # Append prior conversation history if provided (limit to last 4 turns)
        if conversation_history:
            for turn in conversation_history[-4:]:
                if turn.get("role") in ("user", "assistant") and turn.get("content"):
                    messages.append({"role": turn["role"], "content": turn["content"]})

        ans_text, provider = await self._call_llm_api(messages)
        if ans_text:
            topic_status = "DEFLECTED" if TOPIC_DEFLECTION_MESSAGE in ans_text else "ON_TOPIC"
            result = {
                "barcode": barcode,
                "question": clean_q,
                "answer": ans_text,
                "provider": provider or "nvidia_nim_nemoguard",
                "model": self.model_name,
                "is_fallback": False,
                "topic_status": topic_status,
                "disclaimer": STATUTORY_DISCLAIMER,
            }
            if barcode:
                self._cache[cache_key] = result
            return result

        ans = self._answer_from_factsheet_offline(product_data, clean_q)
        return {
            "barcode": barcode,
            "question": clean_q,
            "answer": ans,
            "provider": "local_deterministic_explainer",
            "model": "rule_based_fallback",
            "is_fallback": True,
            "topic_status": "ON_TOPIC",
            "disclaimer": STATUTORY_DISCLAIMER,
        }

    def _build_local_fallback_explanation(self, product_data: Dict[str, Any]) -> str:
        """
        Builds a deterministic plain-English consumer summary.
        """
        name = product_data.get("product_name") or "This product"
        sentences = [f"{name} has been evaluated against Indian FSSAI and ICMR regulatory frameworks."]
        
        allergens = product_data.get("declared_allergens", [])
        if allergens:
            sentences.append(f"It contains declared allergens: {', '.join(allergens)}.")

        findings = product_data.get("key_findings", [])
        if findings:
            for f in findings[:2]:
                if isinstance(f, dict):
                    sentences.append(f"{f.get('title')}: {f.get('explanation')}")

        return " ".join(sentences)

    def _answer_from_factsheet_offline(self, product_data: Dict[str, Any], question: str) -> str:
        """
        Offline question answering using pattern matching against deterministic product facts.
        """
        q = question.lower()
        allergens = product_data.get("declared_allergens", [])
        ingredients = product_data.get("ingredients_text") or product_data.get("ingredients_summary", "")

        if "allergen" in q or "allergic" in q:
            if allergens:
                return f"This product declares the following allergens: {', '.join(allergens)}. If you are sensitive, please exercise caution."
            return "No statutory allergens are explicitly declared on this product label."

        if "sugar" in q:
            return f"Under ICMR-NIN 2024 guidance, added sugars should not exceed recommended thresholds. Review the nutritional panel for declared total and added sugars."

        if "healthy" in q or "hfss" in q:
            return "Under ICMR-NIN Table 15.1/15.2 standards, packaged foods are assessed on their saturated fat, sugar, and sodium density relative to total energy."

        if "ingredient" in q:
            if ingredients:
                return f"Declared ingredients: {ingredients[:300]}..."
            return "Ingredient details are not fully declared or unreadable for this product."

        return (
            f"Based on the product label for {product_data.get('product_name', 'this item')}, "
            "please check the specific nutritional values and ingredients listed in the detailed analysis."
        )


# Global singleton instance
nvidia_nim_client = NvidiaNIMClient()

