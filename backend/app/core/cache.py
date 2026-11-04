"""
YumSure In-Memory High-Performance TTL & LRU Cache.

Provides microsecond in-memory response caching for barcode product lookups
and multi-engine evaluations, reducing repeated database and external API load.
Thread-safe, zero external dependencies, bounded memory footprint.
"""

import time
import logging
from collections import OrderedDict
from threading import Lock
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class ProductAnalysisCache:
    """
    Thread-safe in-memory cache with Time-To-Live (TTL) expiration
    and Least Recently Used (LRU) capacity eviction.
    """

    def __init__(self, max_size: int = 5000, default_ttl_seconds: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a cached item if present and not expired.
        Promotes accessed key to most recently used.
        """
        now = time.time()
        with self._lock:
            if key not in self._cache:
                # Check L2 Persistent SQLite cache on disk
                try:
                    from app.core.persistent_store import persistent_store
                    cached_dict = persistent_store.get_cached_analysis(key)
                    if cached_dict:
                        from app.schemas.product_analysis import ProductAnalysisResponse
                        analysis_res = ProductAnalysisResponse.model_validate(cached_dict)
                        self._cache[key] = {"data": analysis_res, "expires_at": now + self.default_ttl}
                        self._hits += 1
                        return analysis_res
                except Exception as e:
                    logger.debug("L2 persistent cache lookup skipped: %s", e)

                self._misses += 1
                return None

            entry = self._cache[key]
            if now > entry["expires_at"]:
                # Expired -> prune lazily
                del self._cache[key]
                self._misses += 1
                return None

            # Cache hit: mark recently used (move to end of OrderedDict)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry["data"]

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Stores an item in the cache with the given or default TTL.
        Persists into both L1 in-memory LRU and L2 permanent SQLite disk cache.
        """
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expires_at = time.time() + ttl

        with self._lock:
            if key in self._cache:
                # Update existing and mark recently used
                self._cache[key] = {"data": value, "expires_at": expires_at}
                self._cache.move_to_end(key)
            else:
                # Check LRU capacity bound
                if len(self._cache) >= self.max_size:
                    oldest_key, _ = self._cache.popitem(last=False)
                    self._evictions += 1
                    logger.debug("Evicted oldest cache entry '%s' (capacity: %d)", oldest_key, self.max_size)

                self._cache[key] = {"data": value, "expires_at": expires_at}

        # Persist to L2 SQLite disk cache
        try:
            from app.core.persistent_store import persistent_store
            barcode = key.split(":")[1] if ":" in key else key
            dump = value.model_dump(mode="json") if hasattr(value, "model_dump") else value
            if isinstance(dump, dict):
                persistent_store.set_cached_analysis(key, barcode, dump, ttl)
        except Exception as e:
            logger.debug("L2 persistent cache set skipped: %s", e)

    def invalidate(self, key: str) -> bool:
        """Removes a specific key from cache."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Flushes both L1 in-memory cache and L2 permanent SQLite cache."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
        try:
            from app.core.persistent_store import persistent_store
            persistent_store.clear_cache()
        except Exception:
            pass

    def stats(self) -> Dict[str, Any]:
        """Returns diagnostic telemetry about cache utilization."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_ratio = (self._hits / total_requests * 100.0) if total_requests > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio_pct": round(hit_ratio, 2),
                "evictions": self._evictions,
                "default_ttl_seconds": self.default_ttl,
            }


# Global singleton cache instance for application-wide barcode analysis caching
product_cache = ProductAnalysisCache(max_size=5000, default_ttl_seconds=3600)

