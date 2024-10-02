"""Testing ecephys session operation"""

import os
import unittest
import json
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import List
from slims.internal import Record
from aind_slims_api.models.mouse import SlimsMouseContent
from aind_slims_api.models.ecephys_session import (
    SlimsMouseSessionResult,
    SlimsStreamsResult,
    SlimsStimulusEpochsResult,
    SlimsDomeModuleRdrc,
    SlimsRewardDeliveryRdrc,
    SlimsRewardSpoutsRdrc,
    SlimsGroupOfSessionsRunStep,
    SlimsMouseSessionRunStep, SlimsExperimentRunStepContent, SlimsExperimentRunStep,
)
from aind_slims_api import SlimsClient
from aind_slims_api.operations.ecephys_session import(
    SlimsEcephysSessionOperator,
    EcephysSession
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"

class TestSlimsEcephysSessionOperator(unittest.TestCase):

    @patch('aind_slims_api.operations.ecephys_session.SlimsClient')
    def setUp(cls, mock_client):
        cls.mock_client = mock_client()
        cls.operator = SlimsEcephysSessionOperator(subject_id="123456", slims_client=cls.mock_client)
        with open(
            RESOURCES_DIR / "example_fetch_ecephys_session_result.json", "r"
        ) as f:
            response = [
                Record(json_entity=r, slims_api=cls.mock_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_ecephys_session_result = response

    def test_fetch_sessions_success(self):
        # Mock responses for the various methods in SlimsClient
        # Mock for fetching mouse content
        self.mock_client.fetch_model.return_value = SlimsMouseContent.model_construct(pk=12345)

        # Mock for fetching experiment run step content
        self.mock_client.fetch_models.return_value = [
            SlimsExperimentRunStepContent(pk=0, runstep_pk=3, mouse_pk=12345),
            SlimsExperimentRunStepContent(pk=1, runstep_pk=12, mouse_pk=12345)
        ]

        # Mock for fetching group run step and session run steps
        self.mock_client.fetch_models.side_effect = [
            [SlimsGroupOfSessionsRunStep(pk=101)],  # Mock return for SlimsGroupOfSessionsRunStep
            [SlimsMouseSessionRunStep(pk=1), SlimsMouseSessionRunStep(pk=2)],  # Mock session run steps
            [SlimsStreamsResult(stream_modules_pk=[4])],  # Mock for streams
            [SlimsStimulusEpochsResult()]  # Mock for stimulus epochs
        ]

        # Mock individual fetch_model calls in the correct order for a session
        self.mock_client.fetch_model.side_effect = [
            SlimsMouseContent.model_construct(pk=12345),  # Mock for the mouse
            SlimsExperimentRunStep(pk=3, experimentrun_pk=101),  # Mock for experiment run step
            SlimsMouseSessionResult(pk=12),  # Mock session result for the second session
            SlimsMouseSessionResult(pk=0, reward_delivery_pk=3),  # Mock session result for the first session
            SlimsDomeModuleRdrc(),  # Mock for dome module
            SlimsRewardDeliveryRdrc(pk=3, reward_spouts_pk=5),  # Mock for reward delivery
            SlimsRewardSpoutsRdrc(pk=5)  # Mock for reward spouts
        ]

        # Run the fetch_sessions method
        ecephys_sessions = self.operator.fetch_sessions()

        # Assertions
        self.assertEqual(len(ecephys_sessions), 2)
        self.assertIsInstance(ecephys_sessions[0], EcephysSession)
        self.assertIsNone(ecephys_sessions[1].reward_delivery)

    def test_process_sessions_success(self):
        # Setup mock data for process_sessions
        group_run_step = SlimsGroupOfSessionsRunStep()
        session_run_steps = [
            SlimsMouseSessionRunStep(pk=1),
            SlimsMouseSessionRunStep(pk=2)
        ]
        self.mock_client.fetch_model.side_effect = [
            SlimsMouseSessionResult(pk=1, reward_delivery_pk=2),
            SlimsStreamsResult(stream_modules_pk=[3]),
            SlimsStimulusEpochsResult(),
            SlimsDomeModuleRdrc(),
            SlimsRewardDeliveryRdrc(reward_spouts_pk=4),
            SlimsRewardSpoutsRdrc()
        ]

        # Run the _process_sessions method
        ecephys_sessions = self.operator._process_sessions(group_run_step, session_run_steps)

        # Assertions
        self.assertEqual(len(ecephys_sessions), 2)
        self.assertIsInstance(ecephys_sessions[0], EcephysSession)
        self.assertIsNotNone(ecephys_sessions[0].reward_delivery)

    def test_fetch_sessions_handle_exception(self):
        # Setup mock to raise an exception
        self.mock_client.fetch_model.side_effect = Exception("Fetch error")

        # Call fetch_sessions
        ecephys_sessions = self.operator.fetch_sessions()

        # Assertions
        self.assertEqual(len(ecephys_sessions), 0)  # Expecting no sessions to be fetched on error


if __name__ == "__main__":
    unittest.main()
