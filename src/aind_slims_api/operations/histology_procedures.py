"""Module for operations to fetch SPIM histology specimen procedures"""

import logging
from typing import List, Optional, Tuple

from pydantic import BaseModel

from aind_slims_api import SlimsClient
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


class SlimsWash(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""

    wash_step: Optional[SlimsWashRunStep] = None
    reagents: Optional[List[Tuple[SlimsReagentContent, SlimsSource]]] = []


class SPIMHistologyExpBlock(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""

    protocol: Optional[SlimsProtocolSOP] = None
    washes: Optional[List[SlimsWash]] = None
    experiment_template: Optional[SlimsExperimentTemplate] = None


def fetch_washes(client: SlimsClient, experimentrun_pk: int) -> List[SlimsWash]:
    """Fetches washes for a given experimentrun_pk"""
    wash_run_steps = client.fetch_models(
        SlimsWashRunStep, experimentrun_pk=experimentrun_pk
    )
    washes = [
        SlimsWash(
            wash_step=wash,
            reagents=[
                (
                    reagent,
                    (
                        client.fetch_model(SlimsSource, pk=reagent.source_pk)
                        if reagent.source_pk
                        else None
                    ),
                )
                for reagent in (
                    client.fetch_models(SlimsReagentContent, pk=wash.reagent_pk)
                    if wash.reagent_pk
                    else []
                )
            ],
        )
        for wash in wash_run_steps
    ]
    return washes


def fetch_histology_procedures(
    client: SlimsClient, specimen_id: str
) -> List[SPIMHistologyExpBlock]:
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
    specimen_procedures = []
    sample = client.fetch_model(SlimsSampleContent, mouse_barcode=specimen_id)

    content_runs = client.fetch_models(
        SlimsExperimentRunStepContent, mouse_pk=sample.pk
    )

    for content_run in content_runs:
        try:
            # retrieves content step to find experimentrun_pk
            content_run_step = client.fetch_model(
                SlimsExperimentRunStep, pk=content_run.runstep_pk
            )
            experiment_template = client.fetch_model(
                SlimsExperimentTemplate, pk=content_run_step.experiment_template_pk
            )
            protocol_run_step = client.fetch_model(
                SlimsProtocolRunStep, experimentrun_pk=content_run_step.experimentrun_pk
            )
            protocol_sop = None
            if protocol_run_step.protocol_pk:
                protocol_sop = client.fetch_model(
                    SlimsProtocolSOP, pk=protocol_run_step.protocol_pk
                )
            washes = fetch_washes(
                client, experimentrun_pk=content_run_step.experimentrun_pk
            )
            specimen_procedures.append(
                SPIMHistologyExpBlock(
                    protocol=protocol_sop,  # contains protocol link, name
                    experiment_template=experiment_template,
                    washes=washes,
                )
            )
        except SlimsRecordNotFound as e:
            logging.warning(str(e))
            continue

    return specimen_procedures
