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
)
from aind_slims_api.models.histology import (
    SlimsProtocolSOP,
    SlimsReagentContent,
    SlimsReagentDetailsRdrc,
    SlimsSampleContent,
    SlimsSource,
)


class SlimsReagent(BaseModel):
    """Pydantic model to store Reagent Info"""

    content: Optional[SlimsReagentContent] = None
    source: Optional[SlimsSource] = None
    details: Optional[SlimsReagentDetailsRdrc] = None


class SlimsWash(BaseModel):
    """Pydantic model to store Wash Info"""

    wash_step: Optional[SlimsWashRunStep] = None
    reagents: List[SlimsReagent] = []


class SPIMHistologyExpBlock(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""

    protocol: Optional[SlimsProtocolSOP] = None
    washes: Optional[List[SlimsWash]] = None
    experiment_template: Optional[SlimsExperimentTemplate] = None


def fetch_reagents(client: SlimsClient, reagent_pks: List[int]) -> List[SlimsReagent]:
    """Fetches SlimsReagent objects for given reagent primary keys."""
    reagents = []
    for pk in reagent_pks:
        reagent_content = client.fetch_model(SlimsReagentContent, pk=pk)
        details = (
            client.fetch_model(
                SlimsReagentDetailsRdrc, pk=reagent_content.reagent_ref_pk
            )
            if reagent_content and reagent_content.reagent_ref_pk
            else None
        )
        source = (
            client.fetch_model(SlimsSource, pk=details.manufacturer_pk)
            if details and details.manufacturer_pk
            else None
        )
        reagents.append(
            SlimsReagent(
                content=reagent_content,
                details=details,
                source=source,
            )
        )
    return reagents


def fetch_washes(client: SlimsClient, experimentrun_pk: int) -> List[SlimsWash]:
    """Fetches washes for a given experimentrun_pk."""
    washes = []
    wash_run_steps = client.fetch_models(
        SlimsWashRunStep, experimentrun_pk=experimentrun_pk
    )
    for wash_step in wash_run_steps:
        reagents = (
            fetch_reagents(client, wash_step.reagent_pk) if wash_step.reagent_pk else []
        )
        washes.append(SlimsWash(wash_step=wash_step, reagents=reagents))

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
