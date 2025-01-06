"""Tests methods in ecephys session module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.models.ecephys_session import (
    SlimsMouseSessionResult,
    SlimsStimulusEpochsResult,
    SlimsStreamsResult,
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestEcephysSessionResults(unittest.TestCase):
    """Tests top level methods in mouse module"""

    example_client: SlimsClient
    example_fetch_mouse_response: list[Record]

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_client = example_client
        with open(
            RESOURCES_DIR / "example_fetch_ecephys_session_result.json", "r"
        ) as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_ecephys_session_result = response

        with open(
            RESOURCES_DIR / "example_fetch_ecephys_streams_result.json", "r"
        ) as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_ecephys_streams_result = response

        with open(
            RESOURCES_DIR / "example_fetch_ecephys_stimulus_epochs_result.json", "r"
        ) as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_ecephys_stimulus_epochs_result = response

    @patch("slims.slims.Slims.fetch")
    def test_fetch_ecephys_mouse_session_success(self, mock_fetch: MagicMock):
        """Test fetch_mouse_session when successful"""
        mock_fetch.return_value = self.example_fetch_ecephys_session_result
        session = self.example_client.fetch_model(
            SlimsMouseSessionResult, mouse_pk=3135
        )
        self.assertEqual(
            self.example_fetch_ecephys_session_result[0].json_entity,
            session.json_entity,
        )
        self.assertEqual(session.test_label, "Mouse Session")

    @patch("slims.slims.Slims.fetch")
    def test_fetch_ecephys_streams_success(self, mock_fetch: MagicMock):
        """Test fetch streams when successful"""
        mock_fetch.return_value = self.example_fetch_ecephys_streams_result
        streams = self.example_client.fetch_model(
            SlimsStreamsResult, mouse_session_pk=2329
        )
        self.assertEqual(
            self.example_fetch_ecephys_streams_result[0].json_entity,
            streams.json_entity,
        )
        self.assertEqual(streams.test_label, "Streams")
        self.assertEqual(streams.camera_names, ["Face camera"])

    @patch("slims.slims.Slims.fetch")
    def test_fetch_ecephys_stim_epochs_success(self, mock_fetch: MagicMock):
        """Test fetch stim epochs when successful"""
        mock_fetch.return_value = self.example_fetch_ecephys_stimulus_epochs_result
        stim_epochs = self.example_client.fetch_model(
            SlimsStimulusEpochsResult, mouse_session_pk=2329
        )
        self.assertEqual(
            self.example_fetch_ecephys_stimulus_epochs_result[0].json_entity,
            stim_epochs.json_entity,
        )
        self.assertEqual(stim_epochs.test_label, "Stimulus Epochs")
        self.assertEqual(stim_epochs.laser_name, "Coherent Red Laser")


if __name__ == "__main__":
    unittest.main()
