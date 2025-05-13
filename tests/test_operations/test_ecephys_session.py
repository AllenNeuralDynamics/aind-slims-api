"""Testing ecephys session operation"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from slims.internal import Record

from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.ecephys_session import (
    SlimsBrainStructureRdrc,
    SlimsDomeModuleRdrc,
    SlimsMouseSessionResult,
    SlimsRewardDeliveryRdrc,
    SlimsRewardSpoutsRdrc,
    SlimsStreamsResult,
)
from aind_slims_api.models.experiment_run_step import (
    SlimsExperimentRunStep,
    SlimsExperimentRunStepContent,
    SlimsGroupOfSessionsRunStep,
    SlimsMouseSessionRunStep,
)
from aind_slims_api.models.instrument import SlimsInstrumentRdrc
from aind_slims_api.models.mouse import SlimsMouseContent
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

    def test_fetch_streams(self):
        """Tests streams and modules are fetched successfully"""
        example_stream = [
            SlimsStreamsResult(
                pk=12,
                mouse_session_pk=2329,
                camera_names=["camera1", "camera2"],
                stream_modalities=["Ecephys", "Behavior Videos"],
                stream_modules_pk=[123, 456],
            )
        ]
        self.mock_client.fetch_models.side_effect = [example_stream]
        example_module_1 = SlimsDomeModuleRdrc(pk=123)
        example_module_2 = SlimsDomeModuleRdrc(pk=456)
        self.mock_client.fetch_model.side_effect = [example_module_1, example_module_2]
        streams = self.operator.fetch_streams(session_pk=2329)
        self.assertEqual(len(streams), 1)
        self.assertEqual(len(streams[0].stream_modules), 2)

    def test_fetch_stream_modules(self):
        """Tests that stream modules and structures are fetched successfully"""
        example_module_1 = SlimsDomeModuleRdrc(
            pk=123,
            probe_name="ProbeA",
            primary_targeted_structure_pk=789,
            secondary_targeted_structures_pk=[789],
        )
        example_structure = SlimsBrainStructureRdrc(
            pk=789,
            name="Brain Structure A",
        )
        self.mock_client.fetch_model.side_effect = [
            example_module_1,
            example_structure,
            example_structure,
        ]
        stream_modules = self.operator.fetch_stream_modules(stream_modules_pk=[123])
        self.assertEqual(
            stream_modules[0].primary_targeted_structure, example_structure
        )
        self.assertEqual(len(stream_modules[0].secondary_targeted_structures), 1)

    def test_fetch_reward_data(self):
        """Tests that reward info is fetched successfully"""
        self.mock_client.fetch_model.side_effect = [
            SlimsRewardDeliveryRdrc(
                pk=1011, reward_solution="Water", reward_spouts_pk="1213"
            ),
            SlimsRewardSpoutsRdrc(
                pk=1213,
                spout_side="Right",
                variable_position=True,
            ),
        ]
        reward_info = self.operator.fetch_reward_data(reward_delivery_pk=1011)
        self.assertEqual(reward_info.reward_delivery.reward_solution, "Water")
        self.assertEqual(reward_info.reward_spouts.spout_side, "Right")

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

        with patch("logging.warning") as mock_log_warning:
            fetch_ecephys_sessions(client=self.mock_client, subject_id="67890")
            mock_log_warning.assert_called_with(
                "No record found for SlimsExperimentRunStep with pk=3"
            )


if __name__ == "__main__":
    unittest.main()
