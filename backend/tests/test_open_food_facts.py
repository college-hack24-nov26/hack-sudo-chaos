"""
Unit Tests for OpenFoodFactsClient.

Verifies:
1. Successful product retrieval (status 1 -> FOUND).
2. Product not found (status 0 / 404 -> NOT_FOUND).
3. Request timeout handling (TIMEOUT).
4. Network connection failure handling (NETWORK_ERROR).
5. HTTP 500 / error code handling (HTTP_ERROR).
6. Corrupted / invalid JSON payload handling (INVALID_RESPONSE).
7. Zero unhandled exceptions escaping client boundary.
"""

import unittest
from unittest.mock import patch, MagicMock
import httpx

from app.integrations.open_food_facts import (
    OpenFoodFactsClient,
    OpenFoodFactsStatus,
)


class TestOpenFoodFactsClient(unittest.TestCase):
    def setUp(self):
        self.client = OpenFoodFactsClient(
            base_url="https://world.openfoodfacts.org",
            timeout=3.0,
            connect_timeout=1.0,
        )

    @patch("httpx.Client.get")
    def test_01_product_found(self, mock_get):
        """HTTP 200 with status=1 must return OpenFoodFactsStatus.FOUND."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": 1,
            "status_verbose": "product found",
            "product": {
                "product_name": "Test Snack",
                "brands": "BrandX",
                "nutrition_data_per": "100g",
                "nutriments": {"energy_100g": 400},
            },
        }
        mock_get.return_value = mock_resp

        res = self.client.get_product_sync("8901030825279")

        self.assertEqual(res.status, OpenFoodFactsStatus.FOUND)
        self.assertTrue(res.is_found)
        self.assertEqual(res.product_data["product_name"], "Test Snack")
        self.assertEqual(res.barcode, "8901030825279")

    @patch("httpx.Client.get")
    def test_02_product_not_found_status_zero(self, mock_get):
        """HTTP 200 with status=0 must return OpenFoodFactsStatus.NOT_FOUND."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": 0,
            "status_verbose": "product not found",
        }
        mock_get.return_value = mock_resp

        res = self.client.get_product_sync("9999999999999")

        self.assertEqual(res.status, OpenFoodFactsStatus.NOT_FOUND)
        self.assertFalse(res.is_found)
        self.assertIsNone(res.product_data)

    @patch("httpx.Client.get")
    def test_03_product_not_found_http_404(self, mock_get):
        """HTTP 404 must return OpenFoodFactsStatus.NOT_FOUND."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        res = self.client.get_product_sync("9999999999999")

        self.assertEqual(res.status, OpenFoodFactsStatus.NOT_FOUND)
        self.assertFalse(res.is_found)

    @patch("httpx.Client.get")
    def test_04_request_timeout(self, mock_get):
        """httpx.TimeoutException must return OpenFoodFactsStatus.TIMEOUT without crashing."""
        mock_get.side_effect = httpx.TimeoutException("Connection timed out after 3.0s")

        res = self.client.get_product_sync("8901030825279")

        self.assertEqual(res.status, OpenFoodFactsStatus.TIMEOUT)
        self.assertFalse(res.is_found)
        self.assertIn("timed out", res.error_message)

    @patch("httpx.Client.get")
    def test_05_network_failure(self, mock_get):
        """httpx.NetworkError must return OpenFoodFactsStatus.NETWORK_ERROR without crashing."""
        mock_get.side_effect = httpx.NetworkError("Failed to resolve host")

        res = self.client.get_product_sync("8901030825279")

        self.assertEqual(res.status, OpenFoodFactsStatus.NETWORK_ERROR)
        self.assertFalse(res.is_found)
        self.assertIn("Network failure", res.error_message)

    @patch("httpx.Client.get")
    def test_06_http_500_error(self, mock_get):
        """HTTP 500 error must return OpenFoodFactsStatus.HTTP_ERROR."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 500
        mock_get.return_value = mock_resp

        res = self.client.get_product_sync("8901030825279")

        self.assertEqual(res.status, OpenFoodFactsStatus.HTTP_ERROR)
        self.assertEqual(res.http_status, 500)
        self.assertFalse(res.is_found)

    @patch("httpx.Client.get")
    def test_07_invalid_json_payload(self, mock_get):
        """Corrupted JSON must return OpenFoodFactsStatus.INVALID_RESPONSE."""
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.side_effect = ValueError("Expecting value: line 1 column 1")
        mock_get.return_value = mock_resp

        res = self.client.get_product_sync("8901030825279")

        self.assertEqual(res.status, OpenFoodFactsStatus.INVALID_RESPONSE)
        self.assertFalse(res.is_found)


if __name__ == "__main__":
    unittest.main()

