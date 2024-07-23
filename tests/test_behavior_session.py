"""Tests methods in mouse module"""

import json
import os
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.models.behavior_session import SlimsBehaviorSession
from aind_slims_api.models.instrument import SlimsInstrument
from aind_slims_api.models.mouse import SlimsMouseContent
from aind_slims_api.models.user import SlimsUser

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestBehaviorSession(unittest.TestCase):
    """Tests top level methods in mouse module"""

    example_client: SlimsClient
    example_response: list[Record]
    example_mouse_response: list[Record]
    example_behavior_sessions: list[SlimsBehaviorSession]
    example_mouse: SlimsMouseContent
    example_write_sessions_response: Record
    example_instrument: SlimsInstrument
    example_trainer: SlimsUser

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
                    RESOURCES_DIR
                    / (
                        "example_fetch_behavior_session_content_events_response"
                        ".json_entity.json"
                    )
                ).read_text()
            )
        ]
        cls.example_mouse_response = [
            Record(json_entity=r, slims_api=cls.example_client.db.slims_api)
            for r in json.loads(
                (RESOURCES_DIR / "example_fetch_mouse_response.json").read_text()
            )
        ]
        assert (
            len(cls.example_response) > 1
        ), "Example response must be greater than 1 for tests to work..."

        cls.example_instrument = SlimsInstrument(
            nstr_name="323_EPHYS1_OPTO",
            nstr_pk=1,
        )
        cls.example_trainer = SlimsUser(
            user_userName="ClarkR",
            user_pk=1,
        )
        cls.example_mouse = SlimsMouseContent(
            cntn_barCode="00000000",
            cntn_pk=1,
            cntn_cf_waterRestricted=False,
            cntn_cf_scientificPointOfContact=None,
            cntn_cf_baselineWeight=None,
        )
        cls.example_behavior_sessions = [
            SlimsBehaviorSession(
                cnvn_cf_notes="Test notes",
                cnvn_cf_taskStage="Test stage",
                cnvn_cf_task="Test task",
                cnvn_cf_scheduledDate=datetime(2021, 1, 2),
            ),
        ]
        cls.example_write_sessions_response = [
            Record(json_entity=r, slims_api=cls.example_client.db.slims_api)
            for r in json.loads(
                (
                    RESOURCES_DIR
                    / (
                        "example_write_behavior_session_content_events_response."
                        "json_entity.json"
                    )
                ).read_text()
            )
        ][0]

    @patch("slims.slims.Slims.fetch")
    def test_fetch_behavior_session_content_events_success(self, mock_fetch: MagicMock):
        """Test fetch_behavior_session_content_events when successful"""
        mock_fetch.return_value = self.example_response
        validated = self.example_client.fetch_models(
            SlimsBehaviorSession,
            mouse_pk=self.example_mouse.pk,
            sort="date",
        )
        self.assertEqual(
            [item.json_entity for item in self.example_response],
            [item.json_entity for item in validated],
        )

    @patch("slims.slims.Slims.fetch")
    def test_fetch_behavior_session_content_events_success_sort_list(
        self, mock_fetch: MagicMock
    ):
        """Test fetch_behavior_session_content_events when successful"""
        mock_fetch.return_value = self.example_response
        validated = self.example_client.fetch_models(
            SlimsBehaviorSession,
            mouse_pk=self.example_mouse.pk,
            sort=["date"],
        )
        self.assertEqual(
            [item.json_entity for item in self.example_response],
            [item.json_entity for item in validated],
        )


if __name__ == "__main__":
    unittest.main()
