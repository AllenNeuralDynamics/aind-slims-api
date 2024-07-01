"""Tests methods in mouse module"""

import json
import os
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.instrument import (
    fetch_instrument_content,
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestInstrument(unittest.TestCase):
    """Tests top level methods in mouse module"""

    example_client: SlimsClient
    example_response: Record

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        cls.example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_response = [
            Record(json_entity=r, slims_api=cls.example_client.db.slims_api)
            for r in json.loads(
                (
                    RESOURCES_DIR / "example_fetch_instrument_response.json_entity.json"
                ).read_text()
            )
        ]

    @patch("logging.Logger.warning")
    @patch("slims.slims.Slims.fetch")
    def test_fetch_content_success(
        self,
        mock_fetch: MagicMock,
        mock_log_warn: MagicMock,
    ):
        """Test fetch_instrument_content when successful and multiple are
        returned from fetch
        """
        mock_fetch.return_value = self.example_response + self.example_response
        response = fetch_instrument_content(self.example_client, "323_EPHYS1_OPTO")
        self.assertEqual(response.json_entity, self.example_response[0].json_entity)
        self.assertTrue(mock_log_warn.called)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_fail(
        self,
        mock_fetch: MagicMock,
    ):
        """Test fetch_instrument_content when invalid instrument name is given."""
        mock_fetch.return_value = []
        response = fetch_instrument_content(
            self.example_client, "Hopefully not a valid instrument name right?"
        )
        self.assertTrue(response is None)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_unvalidated_success(
        self,
        mock_fetch: MagicMock,
    ):
        """Test fetch_instrument_content when unvalidated instrument data
        returned.
        """
        bad_return = deepcopy(self.example_response[0])
        bad_return.nstr_pk.value = "burrito"
        mock_fetch.return_value = [bad_return, bad_return]
        response = fetch_instrument_content(self.example_client, "323_EPHYS1_OPTO")
        self.assertTrue(isinstance(response, dict))


if __name__ == "__main__":
    unittest.main()
