"""Module for operations to fetch SPIM histology specimen procedures"""

# TODO: figure out which model has modified by and make sure to use it (maybe make a list from washes)

from aind_slims_api import SlimsClient
import logging
from aind_slims_api.models.experiment_run_step import (
    SlimsWashRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentRunStep, SlimsProtocolRunStep, SlimsExperimentTemplate
)
from aind_slims_api.models.histology import SlimsSampleContent, SlimsReagentContent, SlimsProtocolSOP
from aind_slims_api.exceptions import SlimsRecordNotFound
from pydantic import BaseModel
from typing import Optional, List, Dict

class SlimsWash(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""
    wash: Optional[SlimsWashRunStep]
    reagents: Optional[List[SlimsReagentContent]]

class SlimsSPIMHistologyExpBlock(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""
    protocol: Optional[SlimsProtocolSOP]
    washes: Optional[Dict[SlimsWashRunStep, List[SlimsReagentContent]]]
    experiment_template: Optional[SlimsExperimentTemplate]

def fetch_specimen_procedures(
    client: SlimsClient, subject_id: str):
    """
    Fetch and process all electrophysiology (ecephys) run steps for a given subject.
    Retrieves all electrophysiology sessions associated with the provided subject ID
    and returns a list of EcephysSession objects.

    Parameters
    ----------
    client : SlimsClient
        An instance of SlimsClient used to connect to the SLIMS API.
    subject_id : str
        The ID of the subject (mouse) for which to fetch electrophysiology session data.

    Returns
    -------

    Example
    -------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    """
    specimen_procedures = []
    sample = client.fetch_model(SlimsSampleContent, mouse_barcode=subject_id)

    content_runs = client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=sample.pk)

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
                SlimsProtocolRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk
            )
            if protocol_run_step.protocol_pk:
                protocol_sop = client.fetch_model(
                    SlimsProtocolSOP,
                    pk=protocol_run_step.protocol_pk
                )
            else:
                protocol_sop = None
            wash_run_steps = client.fetch_models(
                SlimsWashRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk
            )
            washes = []
            for wash in wash_run_steps:
                reagents = client.fetch_models(SlimsReagentContent, pk=wash.reagent) if wash.reagent else []
                washes.append(
                    SlimsWash(
                        wash=wash,
                        reagents=reagents,
                    )
                )
            specimen_procedures.append(
                SlimsSPIMHistologyExpBlock(
                specimen_id=subject_id,
                protocol=protocol_sop, # contains protocol link, name
                experiment_template=experiment_template, # contains "purpose"
                washes=washes,
                )
            )
        except SlimsRecordNotFound as e:
            logging.info(str(e))
            continue

    return specimen_procedures