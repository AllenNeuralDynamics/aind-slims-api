"""Module for operations to fetch SPIM histology specimen procedures"""

#TODO: Decide whether operations should just be refactored into metadata-service?
#TODO: Look into whether antibodies need more api calls

# Content -> ExperimentRunStepContent -> ExperimentRunStep -> ProtocolRun.
# The protocol runs contain reagant multiselect field, and antibody info
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
from typing import Optional, List

class SlimsWash(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""
    wash: Optional[SlimsWashRunStep]
    reagents: Optional[List[SlimsReagentContent]]

class SlimsSPIMHistologyExpBlock(BaseModel):
    """Pydantic model to store Specimen Procedure Info"""
    specimen_id: str
    protocol: Optional[SlimsProtocolSOP]
    washes: Optional[List[SlimsWash]]

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
            # TODO: group here by step instead of wash. make wash a list per step
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
                # TODO: get example metadata ids with specimen procedures
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

# mappings will be moved to aind-metadata-service
# wash_schema = SpecimenProcedure.model_construct(
#     procedure_type=map_procedure_type(wash.spim_wash_type), # method to map these
#     procedure_name=wash.name,
#     start_date=wash.start_time.date(),
#     end_date=wash.end_time.date(),
#     experimenter_full_name=None, # CHECK IF THIS IS MODIFIED BY,
#     protocol_id=[], # protocol_sop.name = protocol name, might be able to get protocol_id
#     reagents=map_reagents(wash.reagents),
#     antibodies=map_antibodies(wash.wash), # if wash.name is "Primary Antibody Wash" or "Secondary Antibody Wash", Conjugate?
#     # sectioning?
# )