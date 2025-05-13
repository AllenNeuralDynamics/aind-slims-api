"""Tests methods in spim imaging operation"""

import unittest
from unittest.mock import patch
from aind_slims_api.operations.spim_imaging import (
    fetch_imaging_metadata,
    _extract_protocol_link,
)
from aind_slims_api.models.experiment_run_step import (
    SlimsExperimentRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentTemplate,
    SlimsProtocolRunStep,
    SlimsSPIMImagingRunStep,
)
from aind_slims_api.models.imaging import (
    SlimsImagingMetadataResult,
    SlimsSPIMBrainOrientationRdrc,
)
from aind_slims_api.models import (
    SlimsInstrumentRdrc,
    SlimsUser,
    SlimsSampleContent,
    SlimsProtocolSOP,
)
from aind_slims_api.exceptions import SlimsRecordNotFound
from datetime import datetime


class TestFetchImagingMetadata(unittest.TestCase):
    """Test class for fetch_imaging_metadata operation."""

    @patch("aind_slims_api.operations.spim_imaging.SlimsClient")
    def setUp(self, mock_client):
        """Setup test class"""
        self.client = mock_client()

        # Mock sample data
        self.example_sample_content = SlimsSampleContent(
            pk=1, mouse_barcode="000000", barcode="000001"
        )
        self.example_run_step = SlimsExperimentRunStep(
            experiment_template_pk=1426, experimentrun_pk=789
        )
        self.example_experiment_template = SlimsExperimentTemplate(
            pk=1426, name="SPIMImaging"
        )
        self.example_protocol_run_step = SlimsProtocolRunStep(protocol_pk=101)
        self.example_protocol_sop = SlimsProtocolSOP(pk=101, name="Some Protocol SOP")
        self.imaging_step = SlimsSPIMImagingRunStep(pk=6)
        self.imaging_result = SlimsImagingMetadataResult(
            pk=7,
            instrument_json_pk=8,
            surgeon_pk=9,
            brain_orientation_pk=10,
            date_performed=datetime(2024, 10, 18, 22, 27),
            chamber_immersion_medium="Cargille Oil 1.5200",
            sample_immersion_medium="EasyIndex",
            chamber_refractive_index=1.5178,
            sample_refractive_index=1.5180,
        )
        self.instrument = SlimsInstrumentRdrc(pk=8, name="Instrument A")
        self.surgeon = SlimsUser(pk=9, full_name="Surgeon 1", username="surgeon1")
        self.brain_orientation = SlimsSPIMBrainOrientationRdrc(
            pk=10,
            name="Horizontal, Superior; AP",
            x_direction="Left to Right",
            y_direction="Anterior to Posterior",
            z_direction="Superior to Inferior",
        )
        self.expected_metadata = {
            "specimen_id": "000001",
            "subject_id": "000000",
            "protocol_name": "Some Protocol SOP",
            "protocol_id": None,
            "date_performed": datetime(2024, 10, 18, 22, 27),
            "chamber_immersion_medium": "Cargille Oil 1.5200",
            "sample_immersion_medium": "EasyIndex",
            "chamber_refractive_index": 1.5178,
            "sample_refractive_index": 1.5180,
            "instrument_id": "Instrument A",
            "experimenter_name": "Surgeon 1",
            "z_direction": "Superior to Inferior",
            "y_direction": "Anterior to Posterior",
            "x_direction": "Left to Right",
        }

    def test_fetch_imaging_metadata_success(self):
        """ "Tests fetch imaging operation succeeds."""
        self.client.fetch_model.side_effect = lambda model, **kwargs: (
            self.example_sample_content
            if model == SlimsSampleContent
            else (
                self.example_run_step
                if model == SlimsExperimentRunStep
                else (
                    self.example_experiment_template
                    if model == SlimsExperimentTemplate
                    else (
                        self.example_protocol_run_step
                        if model == SlimsProtocolRunStep
                        else (
                            self.example_protocol_sop
                            if model == SlimsProtocolSOP
                            else None
                        )
                    )
                )
            )
        )
        self.client.fetch_models.side_effect = lambda model, **kwargs: (
            [SlimsExperimentRunStepContent(runstep_pk=123)]
            if model == SlimsExperimentRunStepContent
            else (
                [self.imaging_step]
                if model == SlimsSPIMImagingRunStep
                else (
                    [self.imaging_result]
                    if model == SlimsImagingMetadataResult
                    else (
                        [self.instrument]
                        if model == SlimsInstrumentRdrc
                        else (
                            [self.surgeon]
                            if model == SlimsUser
                            else (
                                [self.brain_orientation]
                                if model == SlimsSPIMBrainOrientationRdrc
                                else []
                            )
                        )
                    )
                )
            )
        )

        metadata = fetch_imaging_metadata(self.client, "000000")
        self.assertEqual(len(metadata), 1)
        self.assertEqual(metadata[0], self.expected_metadata)

    def test_fetch_imaging_metadata_no_content(self):
        """Tests case when specimen has no content runs"""
        self.client.fetch_model.return_value = self.example_sample_content
        self.client.fetch_models.side_effect = lambda model, **kwargs: {
            SlimsExperimentRunStepContent: [],
        }.get(model, [])

        metadata = fetch_imaging_metadata(self.client, "000000")
        self.assertEqual(metadata, [])

    def test_fetch_imaging_metadata_missing_record(self):
        """Tests that exception is handled as expected"""
        self.client.fetch_models.side_effect = [
            [SlimsExperimentRunStepContent(pk=1, runstep_pk=3, mouse_pk=67890)]
        ]
        self.client.fetch_model.side_effect = [
            SlimsSampleContent.model_construct(pk=67890),
            SlimsRecordNotFound("No record found for SlimsExperimentRunStep with pk=3"),
        ]

        with patch("logging.warning") as mock_log_warning:
            fetch_imaging_metadata(client=self.client, subject_id="67890")
            mock_log_warning.assert_called_with(
                "No record found for SlimsExperimentRunStep with pk=3"
            )

    def test_extract_protocol_link(self):
        """Tests that protocol link is extracted from html string correctly"""

        protocol_html = '<a href="https://example.com">Example</a>'
        self.assertEqual(_extract_protocol_link(protocol_html), "https://example.com")

        protocol_html = "<a>Missing Href</a>"
        self.assertIsNone(_extract_protocol_link(protocol_html))

        protocol_html = "Not in HTML"
        self.assertEqual(_extract_protocol_link(protocol_html), "Not in HTML")


if __name__ == "__main__":
    unittest.main()
