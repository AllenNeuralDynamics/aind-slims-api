"""Testing ecephys session operation"""

import os
import unittest
import json
from unittest.mock import patch
from pathlib import Path
from slims.internal import Record
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.mouse import SlimsMouseContent
from aind_slims_api.models.ecephys_session import (
    SlimsMouseSessionResult,
    SlimsStreamsResult,
    SlimsDomeModuleRdrc,
    SlimsRewardDeliveryRdrc,
    SlimsRewardSpoutsRdrc,
    SlimsGroupOfSessionsRunStep,
    SlimsMouseSessionRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentRunStep,
    SlimsBrainStructureRdrc,
)
from aind_slims_api.models.instrument import SlimsInstrumentRdrc
from aind_slims_api.operations import EcephysSession, fetch_ecephys_sessions
from aind_slims_api.operations.ecephys_session import EcephysSessionBuilder

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"


class TestSlimsEcephysSessionOperator(unittest.TestCase):
    """Test class for SlimsEcephysSessionOperator"""

    @patch("aind_slims_api.operations.ecephys_session.SlimsClient")
    def setUp(cls, mock_client):
        """setup test class"""
        cls.mock_client = mock_client()
        with open(
            RESOURCES_DIR / "example_fetch_ecephys_session_result.json", "r"
        ) as f:
            response = [
                Record(json_entity=r, slims_api=cls.mock_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_ecephys_session_result = response
        cls.operator = EcephysSessionBuilder(client=cls.mock_client)

    def test_fetch_ecephys_sessions_success(self):
        """Tests session info is fetched successfully"""
        self.mock_client.fetch_models.side_effect = [
            [SlimsExperimentRunStepContent(pk=1, runstep_pk=3, mouse_pk=12345)],
            [SlimsMouseSessionRunStep(pk=7, experimentrun_pk=101)],
            None,
            [
                SlimsStreamsResult(
                    pk=8,
                    mouse_session_pk=7,
                    stream_modules_pk=[9, 10],
                    daq_names=["DAQ1", "DAQ2"],
                )
            ],
            [],
        ]

        self.mock_client.fetch_model.side_effect = [
            SlimsMouseContent.model_construct(pk=12345),
            SlimsExperimentRunStep(pk=3, experimentrun_pk=101),
            SlimsGroupOfSessionsRunStep(
                pk=6,
                session_type="OptoTagging",
                mouse_platform_name="Platform1",
                experimentrun_pk=101,
                instrument_pk=18,
            ),
            SlimsMouseSessionResult(pk=12, reward_delivery_pk=14),
            SlimsInstrumentRdrc(pk=18, name="323InstrumentA"),
            SlimsDomeModuleRdrc(pk=9, probe_name="Probe1", arc_angle=20),
            SlimsDomeModuleRdrc(pk=10, probe_name="Probe1", arc_angle=20),
            SlimsRewardDeliveryRdrc(
                pk=3, reward_spouts_pk=5, reward_solution="Solution1"
            ),
            SlimsRewardSpoutsRdrc(pk=5, spout_side="Left"),
        ]

        # Run the fetch_sessions method
        ecephys_sessions = fetch_ecephys_sessions(
            client=self.mock_client, subject_id="12345"
        )

        # Assertions
        self.assertEqual(len(ecephys_sessions), 1)
        ecephys_session = ecephys_sessions[0]
        self.assertIsInstance(ecephys_session, EcephysSession)
        self.assertEqual(ecephys_session.session_group.session_type, "OptoTagging")
        self.assertEqual(len(ecephys_session.streams), 1)
        self.assertEqual(ecephys_session.streams[0].daq_names, ["DAQ1", "DAQ2"])
        self.assertEqual(len(ecephys_session.streams[0].stream_modules), 2)
        self.assertEqual(ecephys_session.stimulus_epochs, [])

    def test_fetch_ecephys_sessions_handle_exception(self):
        """Tests that exception is handled as expected"""
        self.mock_client.fetch_models.side_effect = [
            [SlimsExperimentRunStepContent(pk=1, runstep_pk=3, mouse_pk=67890)]
        ]
        self.mock_client.fetch_model.side_effect = [
            SlimsMouseContent.model_construct(pk=67890),
            SlimsRecordNotFound("No record found for SlimsExperimentRunStep with pk=3"),
        ]

        with patch("logging.info") as mock_log_info:
            fetch_ecephys_sessions(client=self.mock_client, subject_id="67890")
            mock_log_info.assert_called_with(
                "No record found for SlimsExperimentRunStep with pk=3"
            )


if __name__ == "__main__":
    unittest.main()
