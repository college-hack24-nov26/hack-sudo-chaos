"""
External API Integrations for YumSure.

Provides robust, timeout-bounded clients for third-party food data providers.
"""

from app.integrations.open_food_facts import (
    OpenFoodFactsClient,
    OpenFoodFactsResponse,
    OpenFoodFactsStatus,
)

__all__ = [
    "OpenFoodFactsClient",
    "OpenFoodFactsResponse",
    "OpenFoodFactsStatus",
]
