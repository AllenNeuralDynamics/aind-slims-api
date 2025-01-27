"""Module for operations to fetch SPIM histology specimen procedures"""

import logging
from typing import List, Optional

from pydantic import BaseModel

from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.experiment_run_step import (
    SlimsExperimentRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentTemplate,
    SlimsProtocolRunStep,
    SlimsWashRunStep,
    SlimsSPIMImagingRunStep
)
from aind_slims_api.models.histology import (
    SlimsProtocolSOP,
    SlimsSampleContent,
)

from aind_slims_api.models.imaging import SlimsImagingMetadata


def fetch_imaging_acquisitions(
    client: SlimsClient, specimen_id: str
):
    """
    Fetch and process all spim histology run steps for a given specimen id.
    Retrieves all SPIM histology steps associated with the provided specimen
    and returns a list of SPIMHistologyExpBlock objects.

    Parameters
    ----------
    client : SlimsClient
        An instance of SlimsClient used to connect to the SLIMS API.
    specimen_id : str
        The ID of the specimen for which to fetch histology data.

    Returns
    -------

    Example
    -------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    >>> specimen_procedures = fetch_histology_procedures(client, "000000")
    """
    imaging_acquisitions = []
    sample = client.fetch_model(SlimsSampleContent, mouse_barcode=specimen_id)

    content_runs = client.fetch_models(
        SlimsExperimentRunStepContent, mouse_pk=sample.pk
    )
    # TODO: see if there's any info actually needed from the step or experiment template
    # TODO: see if there's anything in content run itself that can signify imaging 
    for content_run in content_runs:
        try:
            # retrieves content step to find experimentrun_pk
            content_run_step = client.fetch_model(
                SlimsExperimentRunStep, pk=content_run.runstep_pk
            )
            experiment_template = client.fetch_model(
                SlimsExperimentTemplate, pk=content_run_step.experiment_template_pk
            )
            if experiment_template.name == "SPIM Imaging":
                protocol_run_step = client.fetch_model(
                    SlimsProtocolRunStep, experimentrun_pk=content_run_step.experimentrun_pk
                )
                protocol_sop = None
                if protocol_run_step.protocol_pk:
                    protocol_sop = client.fetch_model(
                        SlimsProtocolSOP, pk=protocol_run_step.protocol_pk
                    )
                # imaging_step = client.fetch_models(SlimsSPIMImagingRunStep, experimentrun_pk=content_run_step.experimentrun_pk)
                imaging_result = client.fetch_models(SlimsImagingMetadata, experiment_run_pk=content_run_step.experimentrun_pk)
                imaging_acquisitions.append(
                    {
                        "protocol_sop": protocol_sop,
                        "imaging_metadata": imaging_result,
                    }
                )
        except SlimsRecordNotFound as e:
            logging.warning(str(e))
            continue

    return imaging_acquisitions
