import unittest
from unittest.mock import MagicMock, patch
from aind_slims_api.operations.spim_imaging import fetch_imaging_metadata
from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound

from aind_slims_api.models.experiment_run_step import (
    SlimsExperimentRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentTemplate,
    SlimsProtocolRunStep,
    SlimsSPIMImagingRunStep
)
from aind_slims_api.models import SlimsInstrumentRdrc, SlimsUser
from aind_slims_api.models.histology import (
    SlimsProtocolSOP,
    SlimsSampleContent,
)
from aind_slims_api.models.imaging import SlimsImagingMetadataResult, SlimsSPIMBrainOrientationRdrc

class TestFetchImagingMetadata(unittest.TestCase):

    @patch('aind_slims_api.SlimsClient')
    def test_fetch_imaging_metadata_success(self, MockSlimsClient):
        client = MockSlimsClient()
        specimen_id = "000000"

        # Mocking the sample
        sample = MagicMock()
        sample.pk = 1
        client.fetch_model.return_value = sample

        # Mocking the content runs
        content_run = MagicMock()
        content_run.runstep_pk = 2
        client.fetch_models.return_value = [content_run]

        # Mocking the content run step
        content_run_step = MagicMock()
        content_run_step.experiment_template_pk = 3
        client.fetch_model.return_value = content_run_step

        # Mocking the experiment template
        experiment_template = MagicMock()
        experiment_template.name = "SPIM Imaging"
        client.fetch_model.return_value = experiment_template

        # Mocking the protocol run step
        protocol_run_step = MagicMock()
        protocol_run_step.protocol_pk = 4
        client.fetch_model.return_value = protocol_run_step

        # Mocking the protocol SOP
        protocol_sop = MagicMock()
        client.fetch_model.return_value = protocol_sop

        # Mocking the imaging steps
        imaging_step = MagicMock()
        imaging_step.pk = 5
        client.fetch_models.return_value = [imaging_step]

        # Mocking the imaging results
        imaging_result = MagicMock()
        imaging_result.instrument_json_pk = 6
        imaging_result.surgeon_pk = 7
        imaging_result.brain_orientation_pk = 8
        client.fetch_models.return_value = [imaging_result]

        # Mocking the instrument
        instrument = MagicMock()
        instrument.name = "Instrument 1"
        client.fetch_models.return_value = [instrument]

        # Mocking the surgeon
        surgeon = MagicMock()
        surgeon.name = "Surgeon 1"
        client.fetch_models.return_value = [surgeon]

        # Mocking the brain orientation
        brain_orientation = MagicMock()
        client.fetch_models.return_value = brain_orientation

        result = fetch_imaging_metadata(client, specimen_id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["protocol_sop"], protocol_sop)
        self.assertEqual(result[0]["imaging_metadata"], imaging_result)
        self.assertEqual(result[0]["instrument"], "Instrument 1")
        self.assertEqual(result[0]["surgeon"], "Surgeon 1")
        self.assertEqual(result[0]["brain_orientation"], brain_orientation)

    @patch('aind_slims_api.SlimsClient')
    def test_fetch_imaging_metadata_no_data(self, MockSlimsClient):
        client = MockSlimsClient()
        specimen_id = "000000"

        # Mocking the sample
        sample = MagicMock()
        sample.pk = 1
        client.fetch_model.return_value = sample

        # Mocking no content runs
        client.fetch_models.return_value = []

        result = fetch_imaging_metadata(client, specimen_id)

        self.assertEqual(result, [])

    @patch('aind_slims_api.SlimsClient')
    def test_fetch_imaging_metadata_record_not_found(self, MockSlimsClient):
        client = MockSlimsClient()
        specimen_id = "000000"

        # Mocking the sample
        sample = MagicMock()
        sample.pk = 1
        client.fetch_model.return_value = sample

        # Mocking the content runs
        content_run = MagicMock()
        content_run.runstep_pk = 2
        client.fetch_models.return_value = [content_run]

        # Mocking the content run step to raise SlimsRecordNotFound
        client.fetch_model.side_effect = SlimsRecordNotFound

        result = fetch_imaging_metadata(client, specimen_id)

        self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()