"""Tests methods in histology procedures operation"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.experiment_run_step import (
    SlimsExperimentRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentTemplate,
    SlimsProtocolRunStep,
    SlimsWashRunStep,
)
from aind_slims_api.models.histology import (
    SlimsProtocolSOP,
    SlimsReagentContent,
    SlimsSampleContent,
    SlimsSource,
)
from aind_slims_api.operations.histology_procedures import (
    SlimsWash,
    fetch_histology_procedures,
    fetch_washes,
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"


class TestHistologyProcedures(unittest.TestCase):
    """Test class for SlimsHistologyProcedures operation."""

    @patch("aind_slims_api.operations.histology_procedures.SlimsClient")
    def setUp(cls, mock_client):
        """setup test class"""
        cls.client = mock_client()

    @patch("aind_slims_api.operations.histology_procedures.SlimsWash")
    def test_fetch_washes(self, mock_slims_wash):
        """Tests washes are fetched successfully"""
        example_reagent_content = SlimsReagentContent(
            pk=123,
            source_pk=456,
            lot_number="EI60",
            reagent_name="rgnt0000000",
            barcode="0000000",
        )
        example_source = SlimsSource(
            pk=456,
            name="AA Opto Electronics",
        )
        example_wash_run_step = SlimsWashRunStep(
            reagent_pk=123,
            experimentrun_pk=789,
            wash_name="Wash 1",
            spim_wash_type="Passive Delipidation",
        )
        self.client.fetch_models.side_effect = lambda model, **kwargs: (
            [example_reagent_content]
            if model == SlimsReagentContent
            else [example_wash_run_step] if model == SlimsWashRunStep else []
        )
        self.client.fetch_model.return_value = example_source

        washes = fetch_washes(self.client, experimentrun_pk=789)
        self.client.fetch_models.assert_any_call(SlimsWashRunStep, experimentrun_pk=789)
        self.client.fetch_models.assert_any_call(SlimsReagentContent, pk=123)
        self.client.fetch_model.assert_called_with(SlimsSource, pk=456)
        mock_slims_wash.assert_called_with(
            wash_step=example_wash_run_step,
            reagents=[(example_reagent_content, example_source)],
        )
        self.assertEqual(len(washes), 1)

    @patch("aind_slims_api.operations.histology_procedures.fetch_washes")
    def test_fetch_histology_procedures(self, mock_fetch_washes):
        """Tests that specimen procedures are fetched as expected."""
        example_sample_content = SlimsSampleContent(
            pk=1, mouse_barcode="000000", barcode="000000"
        )
        example_run_step = SlimsExperimentRunStep(
            experiment_template_pk=1426, experimentrun_pk=789
        )
        example_experiment_template = SlimsExperimentTemplate(pk=1426, name="SmartSPIM")
        example_protocol_run_step = SlimsProtocolRunStep(protocol_pk=101)
        example_protocol_sop = SlimsProtocolSOP(pk=101, name="LifeCanvas Clearing")

        self.client.fetch_model.side_effect = lambda model, **kwargs: (
            example_sample_content
            if model == SlimsSampleContent
            else (
                example_run_step
                if model == SlimsExperimentRunStep
                else (
                    example_experiment_template
                    if model == SlimsExperimentTemplate
                    else (
                        example_protocol_run_step
                        if model == SlimsProtocolRunStep
                        else example_protocol_sop if model == SlimsProtocolSOP else None
                    )
                )
            )
        )

        self.client.fetch_models.side_effect = lambda model, **kwargs: (
            [SlimsExperimentRunStepContent(runstep_pk=i) for i in range(1, 7)]
            if model == SlimsExperimentRunStepContent
            else []
        )

        # Mock fetch_washes to return valid SlimsWash objects
        mock_fetch_washes.side_effect = lambda c, experimentrun_pk: [
            SlimsWash(
                wash_step=SlimsWashRunStep(
                    reagent_pk=123,
                    experimentrun_pk=experimentrun_pk,
                    name=f"Wash {experimentrun_pk}",
                    spim_wash_type="Passive Delipidation",
                ),
                reagents=[
                    (
                        SlimsReagentContent(
                            pk=123,
                            source_pk=456,
                            lot_number="EI60",
                            reagent_name="rgnt0000000",
                            barcode="0000000",
                        ),
                        SlimsSource(pk=456, name="AA Opto Electronics"),
                    )
                ],
            )
            for _ in range(4)  # Simulate 4 washes
        ]
        result = fetch_histology_procedures(self.client, specimen_id="000000")

        self.assertEqual(len(result), 6)
        for result_block in result:
            # Check protocol and experiment template
            self.assertEqual(result_block.protocol.name, "LifeCanvas Clearing")
            self.assertEqual(result_block.experiment_template.pk, 1426)

            # Check if washes have been populated correctly
            self.assertEqual(len(result_block.washes), 4)
            for wash in result_block.washes:
                self.assertIsInstance(wash, SlimsWash)
                self.assertIsNotNone(wash.wash_step)
                self.assertEqual(wash.wash_step.spim_wash_type, "Passive Delipidation")
                self.assertGreater(len(wash.reagents), 0)
                for reagent, source in wash.reagents:
                    self.assertIsInstance(reagent, SlimsReagentContent)
                    self.assertIsInstance(source, SlimsSource)
        # Check attributes of first wash
        first_wash = result[0].washes[0]
        self.assertEqual(first_wash.wash_step.name, "Wash 789")
        self.assertEqual(first_wash.wash_step.experimentrun_pk, 789)
        self.assertEqual(first_wash.reagents[0][0].reagent_name, "rgnt0000000")
        self.assertEqual(first_wash.reagents[0][1].name, "AA Opto Electronics")

    def test_fetch_histology_procedures_handles_exception(self):
        """Tests that exception is handled as expected"""
        self.client.fetch_models.side_effect = [
            [SlimsExperimentRunStepContent(pk=1, runstep_pk=3, mouse_pk=67890)]
        ]
        self.client.fetch_model.side_effect = [
            SlimsSampleContent.model_construct(pk=67890),
            SlimsRecordNotFound("No record found for SlimsExperimentRunStep with pk=3"),
        ]

        with patch("logging.warning") as mock_log_warning:
            fetch_histology_procedures(client=self.client, specimen_id="67890")
            mock_log_warning.assert_called_with(
                "No record found for SlimsExperimentRunStep with pk=3"
            )


if __name__ == "__main__":
    unittest.main()
