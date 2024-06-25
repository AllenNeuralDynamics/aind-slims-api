"""Tests methods in mouse module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from copy import deepcopy

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.mouse import fetch_mouse_content

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestMouse(unittest.TestCase):
    """Tests top level methods in mouse module"""

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_client = example_client
        with open(RESOURCES_DIR / "example_fetch_mouse_response.json", "r") as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_mouse_response = response

    @patch("slims.slims.Slims.fetch")
    def test_fetch_mouse_content_success(self, mock_fetch: MagicMock):
        """Test fetch_mouse_content when successful"""
        mock_fetch.return_value = self.example_fetch_mouse_response
        mouse_details = fetch_mouse_content(self.example_client, mouse_name="123456")
        self.assertEqual(
            self.example_fetch_mouse_response[0].json_entity, mouse_details.json_entity
        )

    @patch("logging.Logger.warning")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_mouse_content_no_mouse(
        self, mock_fetch: MagicMock, mock_log_warn: MagicMock
    ):
        """Test fetch_mouse_content when no mouse is returned"""
        mock_fetch.return_value = []
        mouse_details = fetch_mouse_content(self.example_client, mouse_name="12")
        self.assertIsNone(mouse_details)
        mock_log_warn.assert_called_with("Warning, Mouse not in SLIMS")

    @patch("logging.Logger.warning")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_mouse_content_many_mouse(
        self, mock_fetch: MagicMock, mock_log_warn: MagicMock
    ):
        """Test fetch_mouse_content when too many mice are returned"""
        mock_fetch.return_value = [
            self.example_fetch_mouse_response[0],
            self.example_fetch_mouse_response[0],
        ]
        mouse_details = fetch_mouse_content(self.example_client, mouse_name="123456")
        self.assertEqual(
            self.example_fetch_mouse_response[0].json_entity, mouse_details.json_entity
        )
        mock_log_warn.assert_called_with(
            "Warning, Multiple mice in SLIMS with barcode 123456, using pk=3038"
        )

    @patch("logging.Logger.error")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_mouse_content_validation_fail(
        self, mock_fetch: MagicMock, mock_log_error: MagicMock
    ):
        """Test fetch_mouse when successful"""
        wrong_return = deepcopy(self.example_fetch_mouse_response)
        wrong_return[0].cntn_cf_waterRestricted.value = 14
        mock_fetch.return_value = wrong_return
        mouse_info = fetch_mouse_content(self.example_client, mouse_name="123456")
        self.assertEqual(
            self.example_fetch_mouse_response[0].json_entity,
            mouse_info,
        )
        mock_log_error.assert_called()


if __name__ == "__main__":
    unittest.main()
