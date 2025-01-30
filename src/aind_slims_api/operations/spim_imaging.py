"""Module for operations to fetch SPIM histology specimen procedures"""

import logging
import xml.etree.ElementTree as ET
from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.experiment_run_step import (
    SlimsExperimentRunStep,
    SlimsExperimentRunStepContent,
    SlimsProtocolRunStep,
    SlimsSPIMImagingRunStep,
)
from typing import Dict, List, Optional
from aind_slims_api.models import (
    SlimsInstrumentRdrc,
    SlimsUser,
    SlimsProtocolSOP,
    SlimsSampleContent,
)
from aind_slims_api.models.imaging import (
    SlimsImagingMetadataResult,
    SlimsSPIMBrainOrientationRdrc,
)


def _extract_protocol_link(protocol_html: str) -> Optional[str]:
    """Parses out protocol link"""
    try:
        root = ET.fromstring(protocol_html)
        return root.get("href")
    except ET.ParseError:
        return protocol_html


def fetch_imaging_metadata(client: SlimsClient, subject_id: str) -> List[Dict]:
    """
    Fetch and process all spim imaging run steps for a given subject id.
    Retrieves all SPIM imaging steps associated with the provided specimen
    and returns a list of dictionaries.

    Parameters
    ----------
    client : SlimsClient
        An instance of SlimsClient used to connect to the SLIMS API.
    specimen_id : str
        The ID of the specimen for which to fetch histology data.
    Returns
    -------
    imaging_metadata : List[Dict]
    Example
    -------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    >>> imaging = fetch_imaging_metadata(client, "000000")
    """
    imaging_metadata = []
    sample = client.fetch_model(SlimsSampleContent, mouse_barcode=subject_id)

    content_runs = client.fetch_models(
        SlimsExperimentRunStepContent, mouse_pk=sample.pk
    )
    for content_run in content_runs:
        try:
            # retrieves content step to find experimentrun_pk
            content_run_step = client.fetch_model(
                SlimsExperimentRunStep, pk=content_run.runstep_pk
            )
            protocol_run_step = client.fetch_model(
                SlimsProtocolRunStep, experimentrun_pk=content_run_step.experimentrun_pk
            )
            protocol_sop = None
            if protocol_run_step.protocol_pk:
                protocol_sop = client.fetch_model(
                    SlimsProtocolSOP, pk=protocol_run_step.protocol_pk
                )
            imaging_steps = client.fetch_models(
                SlimsSPIMImagingRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk,
            )
            for step in imaging_steps:
                imaging_results = client.fetch_models(
                    SlimsImagingMetadataResult,
                    experiment_run_step_pk=step.pk,
                    content_pk=sample.pk,
                )
                for imaging_result in imaging_results:
                    instrument = client.fetch_models(
                        SlimsInstrumentRdrc, pk=imaging_result.instrument_json_pk
                    )
                    surgeon = client.fetch_models(
                        SlimsUser, pk=imaging_result.surgeon_pk
                    )
                    brain_orientation = client.fetch_models(
                        SlimsSPIMBrainOrientationRdrc,
                        pk=imaging_result.brain_orientation_pk,
                    )
                    imaging_metadata.append(
                        {
                            "specimen_id": sample.barcode,
                            "subject_id": subject_id,
                            "protocol_name": getattr(protocol_sop, "name", None),
                            "protocol_id": (
                                _extract_protocol_link(protocol_sop.link)
                                if protocol_sop and getattr(protocol_sop, "link", None)
                                else None
                            ),
                            "date_performed": getattr(imaging_result, "date_performed"),
                            "chamber_immersion_medium": getattr(
                                imaging_result, "chamber_immersion_medium"
                            ),
                            "sample_immersion_medium": getattr(
                                imaging_result, "sample_immersion_medium"
                            ),
                            "chamber_refractive_index": getattr(
                                imaging_result, "chamber_refractive_index"
                            ),
                            "sample_refractive_index": getattr(
                                imaging_result, "sample_refractive_index"
                            ),
                            "instrument_id": instrument[0].name if instrument else None,
                            "experimenter_name": (
                                surgeon[0].full_name if surgeon else None
                            ),
                            "z_direction": getattr(
                                brain_orientation[0], "z_direction", None
                            ),
                            "y_direction": getattr(
                                brain_orientation[0], "y_direction", None
                            ),
                            "x_direction": getattr(
                                brain_orientation[0], "x_direction", None
                            ),
                        }
                    )
        except SlimsRecordNotFound as e:
            logging.warning(str(e))
            continue

    return imaging_metadata
