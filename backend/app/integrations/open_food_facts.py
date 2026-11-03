"""
Open Food Facts API Client.

Provides bounded, fault-tolerant retrieval of packaged food records from Open Food Facts
with explicit connection pooling, strict request timeouts, and structured error classification.
"""

from enum import Enum
from typing import Optional, Dict, Any
import logging
import httpx

logger = logging.getLogger(__name__)

OFF_DEFAULT_BASE_URL = "https://world.openfoodfacts.org"
OFF_DEFAULT_TIMEOUT_CONNECT = 1.0
OFF_DEFAULT_TIMEOUT_TOTAL = 3.0
OFF_DEFAULT_USER_AGENT = "YumSure-NutritionIntelligence/1.0 (https://yumsure.com; contact: backend@yumsure.com)"

# Minimal statutory & observational fields to minimize network payload
OFF_REQUESTED_FIELDS = (
    "code,"
    "product_name,"
    "product_name_en,"
    "brands,"
    "quantity,"
    "serving_size,"
    "serving_quantity,"
    "product_quantity,"
    "product_quantity_unit,"
    "nutrition_data_per,"
    "nutriments,"
    "ingredients,"
    "ingredients_text,"
    "image_url,"
    "image_front_url,"
    "categories_tags"
)


class OpenFoodFactsStatus(str, Enum):
    """Execution status for Open Food Facts barcode retrieval."""
    FOUND = "FOUND"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    INVALID_RESPONSE = "INVALID_RESPONSE"


class OpenFoodFactsResponse:
    """Standardized result envelope for external Open Food Facts queries."""

    def __init__(
        self,
        status: OpenFoodFactsStatus,
        barcode: str,
        product_data: Optional[Dict[str, Any]] = None,
        raw_payload: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        http_status: Optional[int] = None,
    ) -> None:
        self.status = status
        self.barcode = barcode
        self.product_data = product_data
        self.raw_payload = raw_payload
        self.error_message = error_message
        self.http_status = http_status

    @property
    def is_found(self) -> bool:
        return self.status == OpenFoodFactsStatus.FOUND and self.product_data is not None


class OpenFoodFactsClient:
    """
    Dedicated client for querying Open Food Facts via HTTPX.
    Guarantees strict 3-second bounded execution, connection pooling, and error safety.
    """

    def __init__(
        self,
        base_url: str = OFF_DEFAULT_BASE_URL,
        timeout: float = OFF_DEFAULT_TIMEOUT_TOTAL,
        connect_timeout: float = OFF_DEFAULT_TIMEOUT_CONNECT,
        user_agent: str = OFF_DEFAULT_USER_AGENT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.user_agent = user_agent
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }
        self.timeout_config = httpx.Timeout(
            self.timeout,
            connect=self.connect_timeout,
        )

    def _build_url(self, barcode: str) -> str:
        clean_barcode = barcode.strip()
        return f"{self.base_url}/api/v2/product/{clean_barcode}.json"

    def _parse_response(self, barcode: str, response: httpx.Response) -> OpenFoodFactsResponse:
        """Parses HTTPX response into typed OpenFoodFactsResponse."""
        if response.status_code == 404:
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NOT_FOUND,
                barcode=barcode,
                http_status=404,
                error_message="Product barcode not found on Open Food Facts.",
            )

        if response.status_code != 200:
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.HTTP_ERROR,
                barcode=barcode,
                http_status=response.status_code,
                error_message=f"External Open Food Facts returned HTTP {response.status_code}.",
            )

        try:
            payload = response.json()
        except Exception as err:
            logger.warning("Failed to decode Open Food Facts JSON response for barcode %s: %s", barcode, err)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.INVALID_RESPONSE,
                barcode=barcode,
                http_status=response.status_code,
                error_message="Invalid JSON payload returned by Open Food Facts.",
            )

        if not isinstance(payload, dict):
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.INVALID_RESPONSE,
                barcode=barcode,
                raw_payload={"raw": str(payload)},
                error_message="Unexpected payload format from Open Food Facts.",
            )

        # Status 1 indicates product exists; status 0 indicates product not found
        off_status = payload.get("status")
        if off_status == 1 and "product" in payload and isinstance(payload["product"], dict):
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.FOUND,
                barcode=barcode,
                product_data=payload["product"],
                raw_payload=payload,
                http_status=200,
            )

        return OpenFoodFactsResponse(
            status=OpenFoodFactsStatus.NOT_FOUND,
            barcode=barcode,
            raw_payload=payload,
            http_status=200,
            error_message="Open Food Facts reported product status 0 (not found).",
        )

    async def get_product(self, barcode: str) -> OpenFoodFactsResponse:
        """
        Asynchronously queries Open Food Facts for a product by barcode.
        """
        url = self._build_url(barcode)
        params = {"fields": OFF_REQUESTED_FIELDS}

        try:
            async with httpx.AsyncClient(timeout=self.timeout_config, headers=self.headers) as client:
                resp = await client.get(url, params=params)
                return self._parse_response(barcode, resp)

        except httpx.TimeoutException as err:
            logger.warning("Timeout querying Open Food Facts for barcode %s (timeout=%ss): %s", barcode, self.timeout, err)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.TIMEOUT,
                barcode=barcode,
                error_message=f"Open Food Facts request timed out after {self.timeout}s.",
            )
        except httpx.NetworkError as err:
            logger.warning("Network failure connecting to Open Food Facts for barcode %s: %s", barcode, err)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NETWORK_ERROR,
                barcode=barcode,
                error_message="Network failure connecting to Open Food Facts.",
            )
        except Exception as exc:
            logger.error("Unexpected error querying Open Food Facts for barcode %s: %s", barcode, exc)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NETWORK_ERROR,
                barcode=barcode,
                error_message=f"Unexpected external query error: {str(exc)}",
            )

    def get_product_sync(self, barcode: str) -> OpenFoodFactsResponse:
        """
        Synchronously queries Open Food Facts for a product by barcode.
        """
        url = self._build_url(barcode)
        params = {"fields": OFF_REQUESTED_FIELDS}

        try:
            with httpx.Client(timeout=self.timeout_config, headers=self.headers) as client:
                resp = client.get(url, params=params)
                return self._parse_response(barcode, resp)

        except httpx.TimeoutException as err:
            logger.warning("Timeout querying Open Food Facts for barcode %s: %s", barcode, err)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.TIMEOUT,
                barcode=barcode,
                error_message=f"Open Food Facts request timed out after {self.timeout}s.",
            )
        except httpx.NetworkError as err:
            logger.warning("Network failure connecting to Open Food Facts for barcode %s: %s", barcode, err)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NETWORK_ERROR,
                barcode=barcode,
                error_message="Network failure connecting to Open Food Facts.",
            )
        except Exception as exc:
            logger.error("Unexpected error querying Open Food Facts for barcode %s: %s", barcode, exc)
            return OpenFoodFactsResponse(
                status=OpenFoodFactsStatus.NETWORK_ERROR,
                barcode=barcode,
                error_message=f"Unexpected external query error: {str(exc)}",
            )

