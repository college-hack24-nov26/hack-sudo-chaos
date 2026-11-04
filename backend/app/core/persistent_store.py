"""
YumSure Permanent Storage & Persistent SQLite Cache.

Provides local permanent storage for:
1. User Scan History: Persists scan ledger across application restarts.
2. L2 Persistent Product Analysis Cache: Caches evaluation responses on disk with TTL.
3. Local Indian Packaged Foods Dataset Catalog: Indexed from packaged_foods_india.csv
   for sub-millisecond offline product lookups.
"""

import os
import sqlite3
import json
import time
import uuid
import csv
import re
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List, Dict, Any

from app.domain.engines.contracts import (
    FoodForm,
    NutrientDataStatus,
    MeasurementBasis,
    NutrientObservationInput,
    IngredientObservationInput,
    ProductEvaluationInput,
)

logger = logging.getLogger(__name__)

# Default persistent database location
DEFAULT_DB_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "data", "yumsure_persistent.db")
)


class PersistentStore:
    """Thread-safe SQLite persistent store for scan history, analysis cache, and dataset catalog."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initializes tables and indexes if they do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. User Scan History Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_scan_history (
                    id TEXT PRIMARY KEY,
                    barcode TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    brand_name TEXT,
                    food_category TEXT,
                    image_url TEXT,
                    key_finding TEXT,
                    key_finding_severity TEXT,
                    scanned_at TEXT NOT NULL
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_barcode ON user_scan_history(barcode)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scan_history_scanned_at ON user_scan_history(scanned_at DESC)")

            # 2. L2 Persistent Product Analysis Cache Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS persistent_product_cache (
                    cache_key TEXT PRIMARY KEY,
                    barcode TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires_at ON persistent_product_cache(expires_at)")

            # 3. Local Dataset Catalog Table (Packaged Foods India)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS local_dataset_catalog (
                    barcode TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    brand_name TEXT,
                    food_form TEXT NOT NULL,
                    food_category TEXT,
                    package_size TEXT,
                    serving_size_value REAL,
                    serving_size_unit TEXT,
                    nutrients_json TEXT NOT NULL,
                    ingredients_json TEXT NOT NULL,
                    image_url TEXT
                )
                """
            )
            conn.commit()

    # -------------------------------------------------------------------------
    # 1. User Scan History Operations
    # -------------------------------------------------------------------------
    def record_scan(
        self,
        barcode: str,
        product_name: str,
        brand_name: Optional[str] = None,
        food_category: Optional[str] = None,
        image_url: Optional[str] = None,
        key_finding: Optional[str] = None,
        key_finding_severity: str = "MODERATE",
        scanned_at: Optional[datetime] = None,
    ) -> None:
        """Appends a scanned product record into permanent scan history."""
        clean_barcode = barcode.strip()
        timestamp = (scanned_at or datetime.now(timezone.utc)).isoformat()
        record_id = str(uuid.uuid4())

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO user_scan_history (
                        id, barcode, product_name, brand_name, food_category,
                        image_url, key_finding, key_finding_severity, scanned_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record_id,
                        clean_barcode,
                        product_name,
                        brand_name,
                        food_category or "Packaged Food",
                        image_url,
                        key_finding,
                        key_finding_severity,
                        timestamp,
                    ),
                )
                conn.commit()
        except Exception as e:
            logger.warning("Failed to record scan history in SQLite: %s", e)

    def get_recent_scans(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieves most recent scan records ordered by scanned_at descending."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, barcode, product_name, brand_name, food_category,
                           image_url, key_finding, key_finding_severity, scanned_at
                    FROM user_scan_history
                    ORDER BY scanned_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "barcode": row["barcode"],
                        "product_name": row["product_name"],
                        "brand_name": row["brand_name"],
                        "food_category": row["food_category"],
                        "image_url": row["image_url"],
                        "key_finding": row["key_finding"],
                        "key_finding_severity": row["key_finding_severity"],
                        "scanned_at": row["scanned_at"],
                    })
                return results
        except Exception as e:
            logger.warning("Failed to read scan history from SQLite: %s", e)
            return []

    # -------------------------------------------------------------------------
    # 2. L2 Persistent Product Analysis Cache Operations
    # -------------------------------------------------------------------------
    def get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieves unexpired analysis payload from permanent SQLite cache."""
        now = time.time()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT payload_json, expires_at
                    FROM persistent_product_cache
                    WHERE cache_key = ?
                    """,
                    (cache_key,),
                )
                row = cursor.fetchone()
                if not row:
                    return None
                if now > row["expires_at"]:
                    # Prune expired entry
                    cursor.execute("DELETE FROM persistent_product_cache WHERE cache_key = ?", (cache_key,))
                    conn.commit()
                    return None
                return json.loads(row["payload_json"])
        except Exception as e:
            logger.debug("Failed to read persistent cache for %s: %s", cache_key, e)
            return None

    def set_cached_analysis(
        self,
        cache_key: str,
        barcode: str,
        payload_dict: Dict[str, Any],
        ttl_seconds: int = 86400,
    ) -> None:
        """Persists analysis payload dictionary into SQLite with TTL (default: 24 hours)."""
        now = time.time()
        expires_at = now + ttl_seconds
        payload_json = json.dumps(payload_dict)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO persistent_product_cache (
                        cache_key, barcode, payload_json, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(cache_key) DO UPDATE SET
                        payload_json = excluded.payload_json,
                        created_at = excluded.created_at,
                        expires_at = excluded.expires_at
                    """,
                    (cache_key, barcode.strip(), payload_json, now, expires_at),
                )
                conn.commit()
        except Exception as e:
            logger.warning("Failed to write persistent cache for %s: %s", cache_key, e)

    def clear_cache(self) -> None:
        """Flushes all persistent cache records."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM persistent_product_cache")
                conn.commit()
        except Exception as e:
            logger.warning("Failed to clear persistent cache: %s", e)

    # -------------------------------------------------------------------------
    # 3. Local Dataset Catalog Operations (Packaged Foods India)
    # -------------------------------------------------------------------------
    def load_dataset_csv_if_empty(self, csv_path: str) -> int:
        """
        Indexes packaged_foods_india.csv into SQLite catalog if table is empty.
        Returns total indexed count.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM local_dataset_catalog")
                cnt = cursor.fetchone()["count"]
                if cnt > 0:
                    return cnt
        except Exception:
            pass

        if not os.path.exists(csv_path):
            logger.warning("Dataset CSV not found at %s", csv_path)
            return 0

        logger.info("Indexing packaged foods India dataset into persistent SQLite: %s", csv_path)
        indexed = 0

        # Known retail barcodes
        known_barcodes = {
            "Britannia Nutrichoice Digestive High-Fibre Biscuits": "8901030383701",
            "Britannia Nutrichoice Digestive High-Fibre Biscuits": "8901030383701",
            "HIDE & SEEK® ": "8901719101038",
            "HIDE & SEEK®": "8901719101038",
            "Sunfeast Dark Fantasy Choco Fills, Original Filled Cookies with Choco Crème": "8901725132224",
            "Britannia Good Day Cashew Cookies Family Pack": "8901063141233",
            "Kissan Fresh Tomato Ketchup": "8901030825279",
            "2-Minute Masala Instant Noodles": "8901058860002",
            "Maggi 2-Minute Masala Noodles": "8901058860002",
        }

        def calculate_ean13(prefix12: str) -> str:
            digits = [int(c) for c in prefix12[:12]]
            odd_sum = sum(digits[i] for i in range(0, 12, 2))
            even_sum = sum(digits[i] for i in range(1, 12, 2))
            total = odd_sum + (even_sum * 3)
            check = (10 - (total % 10)) % 10
            return f"{prefix12[:12]}{check}"

        with open(csv_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for idx, row in enumerate(rows, start=1):
                s_no = row.get("S.No", str(idx)).strip()
                item_name = row.get("Item name", "").strip()
                if not item_name:
                    continue

                brand_name = row.get("Brand_Name", "").strip() or None
                category = row.get("Category", "").strip() or "Packaged Food"
                sub_category = row.get("Sub_Category", "").strip() or ""

                combined = f"{category} {sub_category} {item_name}".lower()
                is_liquid = any(k in combined for k in ("beverage", "juice", "drink", "milk", "water", "sauce", "ketchup", "syrup", "oil", "soda"))
                food_form = "liquid" if is_liquid else "solid"

                barcode = known_barcodes.get(item_name)
                if not barcode:
                    prefix12 = f"8901{int(re.sub(r'[^0-9]', '', s_no) or idx):08d}"
                    barcode = calculate_ean13(prefix12)

                def parse_num(v):
                    if not v:
                        return None
                    m = re.search(r"[-+]?\d*\.?\d+", str(v).replace(",", ""))
                    return float(m.group(0)) if m else None

                serving_val = parse_num(row.get("Serving_Size_g")) or 100.0

                nutrients = {
                    "energy": {"val": parse_num(row.get("Calories_kcal")), "unit": "kcal"},
                    "carbohydrates": {"val": parse_num(row.get("Carbohydrates_g")), "unit": "g"},
                    "protein": {"val": parse_num(row.get("Proteins_g")), "unit": "g"},
                    "total_fat": {"val": parse_num(row.get("Total_Fat_g")), "unit": "g"},
                    "saturated_fat": {"val": parse_num(row.get("Saturated_Fat_g")), "unit": "g"},
                    "trans_fat": {"val": parse_num(row.get("Trans_Fat_g")), "unit": "g"},
                    "total_sugars": {"val": parse_num(row.get("Sugar_g")), "unit": "g"},
                    "sodium": {"val": parse_num(row.get("Sodium_mg")), "unit": "mg"},
                    "dietary_fibre": {"val": parse_num(row.get("Dietary_Fiber_g")), "unit": "g"},
                }

                raw_ings = row.get("Ingredients", "")
                parts = [p.strip() for p in re.split(r",(?![^(]*\))", raw_ings) if p.strip()]
                ingredients = [{"sequence_order": i, "text": p} for i, p in enumerate(parts, start=1)]

                cursor.execute(
                    """
                    INSERT INTO local_dataset_catalog (
                        barcode, product_name, brand_name, food_form, food_category,
                        package_size, serving_size_value, serving_size_unit,
                        nutrients_json, ingredients_json, image_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(barcode) DO UPDATE SET
                        product_name = excluded.product_name,
                        brand_name = excluded.brand_name,
                        food_form = excluded.food_form,
                        food_category = excluded.food_category
                    """,
                    (
                        barcode,
                        item_name,
                        brand_name,
                        food_form,
                        category,
                        f"{serving_val}g",
                        serving_val,
                        "ml" if is_liquid else "g",
                        json.dumps(nutrients),
                        json.dumps(ingredients),
                        None,
                    ),
                )
                indexed += 1

            conn.commit()

        logger.info("Indexed %d packaged food items into persistent SQLite catalog.", indexed)
        return indexed

    def get_catalog_product(self, barcode: str) -> Optional[ProductEvaluationInput]:
        """
        Retrieves a product from the local dataset catalog and constructs
        a canonical ProductEvaluationInput domain DTO.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT barcode, product_name, brand_name, food_form, food_category,
                           package_size, serving_size_value, serving_size_unit,
                           nutrients_json, ingredients_json, image_url
                    FROM local_dataset_catalog
                    WHERE barcode = ?
                    """,
                    (barcode.strip(),),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                food_form = FoodForm.LIQUID if row["food_form"] == "liquid" else FoodForm.SOLID
                basis = MeasurementBasis.PER_100ML if food_form == FoodForm.LIQUID else MeasurementBasis.PER_100G

                nutrients_data = json.loads(row["nutrients_json"])
                nutrients_dict: Dict[str, NutrientObservationInput] = {}

                for code, data in nutrients_data.items():
                    val = data.get("val")
                    unit = data.get("unit", "g")
                    if val is None:
                        status = NutrientDataStatus.NOT_DECLARED
                        dec_val = None
                    elif float(val) == 0.0:
                        status = NutrientDataStatus.EXPLICITLY_ZERO
                        dec_val = Decimal("0.0")
                    else:
                        status = NutrientDataStatus.PRESENT
                        dec_val = Decimal(str(val))

                    nutrients_dict[code] = NutrientObservationInput(
                        nutrient_code=code,
                        per_100g_value=dec_val,
                        per_serving_value=None,
                        unit=unit,
                        data_status=status,
                        measurement_basis=basis,
                    )

                ingredients_data = json.loads(row["ingredients_json"])
                ingredients_list: List[IngredientObservationInput] = []

                for item in ingredients_data:
                    seq = item.get("sequence_order", 1)
                    txt = item.get("text", "")
                    code_slug = re.sub(r"[^\w]", "_", txt.lower())[:50]
                    ingredients_list.append(
                        IngredientObservationInput(
                            ingredient_code=code_slug,
                            declared_label_text=txt,
                            sequence_order=seq,
                        )
                    )

                return ProductEvaluationInput(
                    product_id=row["barcode"],
                    product_name=row["product_name"],
                    brand_name=row["brand_name"],
                    food_form=food_form,
                    food_category=row["food_category"],
                    package_size=row["package_size"],
                    serving_size_value=Decimal(str(row["serving_size_value"])) if row["serving_size_value"] else None,
                    serving_size_unit=row["serving_size_unit"] or "g",
                    nutrients=nutrients_dict,
                    ingredients=ingredients_list,
                    declared_claims=[],
                    data_source_id="packaged_foods_india_catalog",
                )
        except Exception as e:
            logger.warning("Error fetching catalog product %s from SQLite: %s", barcode, e)
            return None


# Global singleton persistent store
persistent_store = PersistentStore()
