"""Module for operations to fetch histology specimen procedures"""
#TODO: decide whether to do this here in operation, or directly map in metadata-service

# Content -> ExperimentRunStepContent -> ExperimentRunStep -> ProtocolRun.
# The protocol runs contain reagant multiselect field, and antibody info
from aind_slims_api import SlimsClient
import logging
from aind_slims_api.models.experiment_run_step import (
    SlimsWashRunStep,
    SlimsExperimentRunStepContent,
    SlimsExperimentRunStep, SlimsProtocolRunStep
)
from aind_slims_api.models.histology import SlimsSampleContent, SlimsReagentContent, SlimsProtocolSOP
from aind_slims_api.exceptions import SlimsRecordNotFound

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
    washes = []
    sample = client.fetch_model(SlimsSampleContent, mouse_barcode=subject_id)
    content_runs = client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=sample.pk)

    for content_run in content_runs:
        try:
            # retrieves content step to find experimentrun_pk
            content_run_step = client.fetch_model(
                SlimsExperimentRunStep, pk=content_run.runstep_pk
            )
            protocol = client.fetch_model(
                SlimsProtocolRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk
            )
            protocol_sop = client.fetch_model(
                SlimsProtocolSOP,
                pk=protocol.pk
            )
            # TODO: protocol_sop.name = protocol name, might be able to get protocol_id from here
            # right now wash run steps has no filter so it also gets protocol. maybe just keep it vague
            # and in the metadata-service, put everything together as necessary
            wash_run_steps = client.fetch_models(
                SlimsWashRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk
            )
            washes.append(wash_run_steps)
            # TODO: for each wash, check if theres reagent -> fetch model

        except SlimsRecordNotFound as e:
            logging.info(str(e))
            continue

