"""Module for operations to fetch histology specimen procedures"""

# Content -> ExperimentRunStepContent -> ExperimentRunStep -> ProtocolRun.
# The protocol runs contain reagant multiselect field, and antibody info
from aind_slims_api import SlimsClient

class HistologyProceduresBuilder:
    """Class to build EcephysSession objects from session run steps."""

    def __init__(self, client: SlimsClient):
        """Initialize Session Builder"""
        self.client = client

    def _process_single_step(self, group_run_step, session_run_step) -> EcephysSession:
        """Process a single session run step into an EcephysSession."""
        session = self.client.fetch_model(
            SlimsMouseSessionResult, experiment_run_step_pk=session_run_step.pk
        )
        session_instrument = self.client.fetch_model(
            SlimsInstrumentRdrc, pk=group_run_step.instrument_pk
        )
        stimulus_epochs = self.client.fetch_models(
            SlimsStimulusEpochsResult, mouse_session_pk=session.pk
        )

        streams = self.fetch_streams(session.pk)
        reward_delivery = (
            self.fetch_reward_data(session.reward_delivery_pk)
            if session.reward_delivery_pk
            else None
        )

        return EcephysSession(
            session_group=group_run_step,
            session_instrument=session_instrument or None,
            session_result=session,
            streams=streams or None,
            reward_delivery=reward_delivery,
            stimulus_epochs=stimulus_epochs or [],
        )

    def process_session_steps(
        self,
        group_run_step: SlimsGroupOfSessionsRunStep,
        session_run_steps: List[SlimsMouseSessionRunStep],
    ) -> List[EcephysSession]:
        """
        Processes all session run steps into EcephysSession objects.
        Parameters
        ----------
        group_run_step : SlimsGroupOfSessionsRunStep
            The group run step containing session metadata and run information.
        session_run_steps : List[SlimsMouseSessionRunStep]
            A list of individual session run steps to be processed and encapsulated.

        Returns
        -------
        List[EcephysSession]
            A list of EcephysSession objects containing the processed session data.
        """
        return [
            self._process_single_step(group_run_step, step)
            for step in session_run_steps
        ]


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
    histology_specimen_procedures = []
    # TODO: Instead of SlimsMouseContent, SlimsSpecimenContent
    mouse = client.fetch_model(SlimsMouseContent, barcode=subject_id)
    content_runs = client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=mouse.pk)

    for content_run in content_runs:
        try:
            # retrieves content step to find experimentrun_pk
            content_run_step = client.fetch_model(
                SlimsExperimentRunStep, pk=content_run.runstep_pk
            )

        except SlimsRecordNotFound as e:
            logging.info(str(e))
            continue

    # return ecephys_sessions_list
