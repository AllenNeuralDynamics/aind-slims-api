"""Tests methods in user module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.user import fetch_user

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestUser(unittest.TestCase):
    """Tests top level methods in user module"""

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_client = example_client
        with open(RESOURCES_DIR / "example_fetch_user_response.json", "r") as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_user_response = response

    @patch("slims.slims.Slims.fetch")
    def test_fetch_user_content_success(self, mock_fetch: MagicMock):
        """Test fetch_user when successful"""
        mock_fetch.return_value = self.example_fetch_user_response
        user_info = fetch_user(self.example_client, username="PersonA")
        self.assertEqual(self.example_fetch_user_response[0].json_entity, user_info)

    @patch("logging.Logger.warning")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_user_content_no_user(
        self, mock_fetch: MagicMock, mock_log_warn: MagicMock
    ):
        """Test fetch_user when no user is returned"""
        mock_fetch.return_value = []
        user_info = fetch_user(self.example_client, username="PersonX")
        self.assertIsNone(user_info)
        mock_log_warn.assert_called_with("Warning, User not in SLIMS")

    @patch("logging.Logger.warning")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_user_content_many_users(
        self, mock_fetch: MagicMock, mock_log_warn: MagicMock
    ):
        """Test fetch_user_content when too many users are returned"""
        mocked_response = [
            self.example_fetch_user_response[0],
            self.example_fetch_user_response[0],
        ]
        mock_fetch.return_value = mocked_response
        user_info = fetch_user(self.example_client, username="PersonA")
        self.assertEqual(self.example_fetch_user_response[0].json_entity, user_info)
        expected_warning = (
            f"Warning, Multiple users in SLIMS with "
            f"username {[u.json_entity for u in mocked_response]}, "
            f"using pk={mocked_response[0].pk()}"
        )
        mock_log_warn.assert_called_with(expected_warning)


if __name__ == "__main__":
    unittest.main()
