import unittest
from unittest.mock import MagicMock, patch
from aind_slims_api.operations.histology_procedures import (
    fetch_washes,
    fetch_histology_procedures,
    SlimsWash,
    SPIMHistologyExpBlock
)
from aind_slims_api.models.histology import SlimsSampleContent
from aind_slims_api.models.experiment_run_step import (
    SlimsWashRunStep, SlimsExperimentRunStepContent, SlimsExperimentRunStep,
    SlimsProtocolRunStep, SlimsExperimentTemplate
)
from aind_slims_api.models.histology import SlimsReagentContent, SlimsSource, SlimsProtocolSOP
from aind_slims_api.exceptions import SlimsRecordNotFound
from pathlib import Path
import os
from slims.internal import Record
import json

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"

class TestHistologyProcedures(unittest.TestCase):
    """Test class for SlimsHistologyProcedures operation."""

    @patch("aind_slims_api.operations.histology_procedures.SlimsClient")
    def setUp(cls, mock_client):
        """setup test class"""
        cls.client = mock_client()
        # with open(
        #     RESOURCES_DIR / "example_fetch_histology_procedures.json", "r"
        # ) as f:
        #     response = [
        #         Record(json_entity=r, slims_api=cls.client.db.slims_api)
        #         for r in json.load(f)
        #     ]
        # cls.example_fetch_histology_procedures = response
        
    @patch("aind_slims_api.operations.histology_procedures.SlimsWash")
    def test_fetch_washes(self, mock_slims_wash):
        """Tests washes are fetched successfully"""
        example_reagent_content = SlimsReagentContent(
            pk=123,
            source_pk=456,
            lot_number="EI60",
            reagent_name="rgnt0000000",
            barcode="0000000"
        )
        example_source = SlimsSource(
            pk=456,
            name="AA Opto Electronics",
        )
        example_wash_run_step = SlimsWashRunStep(
            reagent_pk=123,
            experimentrun_pk=789,
            wash_name="Wash 1",
            spim_wash_type="Passive Delipidation"
        )
        self.client.fetch_models.side_effect = lambda model, **kwargs: (
            [example_reagent_content] if model == SlimsReagentContent else
            [example_wash_run_step] if model == SlimsWashRunStep else
            []
        )
        self.client.fetch_model.return_value = example_source

        washes = fetch_washes(self.client, experimentrun_pk=789)

        self.client.fetch_models.assert_any_call(SlimsWashRunStep, experimentrun_pk=789)
        self.client.fetch_models.assert_any_call(SlimsReagentContent, pk=123)
        self.client.fetch_model.assert_called_with(SlimsSource, pk=456)
        mock_slims_wash.assert_called_with(
            wash_step=example_wash_run_step,
            reagents=[(example_reagent_content, example_source)]
        )
        self.assertEqual(len(washes), 1)

    @patch('aind_slims_api.operations.histology_procedures.fetch_washes')
    def test_fetch_histology_procedures(self, mock_fetch_washes):
        # Mock data for specimen and content runs
        # TODO: use example_fetch_histology_procedures.json
        mock_sample = SlimsSampleContent(pk=1)
        mock_content_run = SlimsExperimentRunStepContent(runstep_pk=2)
        mock_experiment_run_step = SlimsExperimentRunStep(experiment_template_pk=3, experimentrun_pk=4)
        mock_experiment_template = SlimsExperimentTemplate()
        mock_protocol_run_step = SlimsProtocolRunStep(protocol_pk=5)
        mock_protocol_sop = SlimsProtocolSOP()

        self.client.fetch_model.side_effect = lambda model, **kwargs: {
            SlimsSampleContent: mock_sample,
            SlimsExperimentRunStep: mock_experiment_run_step,
            SlimsExperimentTemplate: mock_experiment_template,
            SlimsProtocolRunStep: mock_protocol_run_step,
            SlimsProtocolSOP: mock_protocol_sop
        }.get(model, None)
        self.client.fetch_models.return_value = [mock_content_run]
        mock_fetch_washes.return_value = []

        procedures = fetch_histology_procedures(self.client, "000000")

        self.client.fetch_model.assert_any_call(SlimsSampleContent, mouse_barcode="000000")
        self.client.fetch_models.assert_called_with(SlimsExperimentRunStepContent, mouse_pk=1)
        self.client.fetch_model.assert_any_call(SlimsExperimentRunStep, pk=2)
        self.client.fetch_model.assert_any_call(SlimsExperimentTemplate, pk=3)
        self.client.fetch_model.assert_any_call(SlimsProtocolRunStep, experimentrun_pk=4)
        self.client.fetch_model.assert_any_call(SlimsProtocolSOP, pk=5)
        mock_fetch_washes.assert_called_with(self.client, experimentrun_pk=4)

        self.assertEqual(len(procedures), 1)
        self.assertIsInstance(procedures[0], SPIMHistologyExpBlock)

#     def test_fetch_histology_procedures_handles_missing_records(self):
#         # Mock raising SlimsRecordNotFound
#         self.client.fetch_model.side_effect = SlimsRecordNotFound("Record not found")
#         self.client.fetch_models.return_value = []

#         procedures = fetch_histology_procedures(self.client, "000000")

#         self.client.fetch_model.assert_called_with(SlimsSampleContent, mouse_barcode="000000")
#         self.assertEqual(len(procedures), 0)

# if __name__ == "__main__":
#     unittest.main()
