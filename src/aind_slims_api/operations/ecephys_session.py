"""
Module defining operations to build EcephysSession.
"""

import logging
from typing import List, Optional
from pydantic import BaseModel

from aind_slims_api import SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.mouse import SlimsMouseContent
from aind_slims_api.models.ecephys_session import (
    SlimsMouseSessionResult,
    SlimsStreamsResult,
    SlimsStimulusEpochsResult,
    SlimsExperimentRunStepContent,
    SlimsExperimentRunStep,
    SlimsDomeModuleRdrc,
    SlimsRewardDeliveryRdrc,
    SlimsRewardSpoutsRdrc,
    SlimsGroupOfSessionsRunStep,
    SlimsMouseSessionRunStep, SlimsBrainStructureRdrc,
)

logger = logging.getLogger(__name__)


class SlimsStreamModule(SlimsDomeModuleRdrc):
    """"""
    primary_targeted_structure: Optional[str] = None
    secondary_targeted_structures: Optional[list[str]] = None


class SlimsStream(SlimsStreamsResult):
    """"""
    stream_modules: List[SlimsStreamModule]

class EcephysSession(BaseModel):
    """
    Pydantic model encapsulating all session-related responses.
    """

    session_group: SlimsExperimentRunStep
    session_result: Optional[SlimsMouseSessionResult]
    streams: Optional[List[SlimsStream]] = []
    reward_delivery: Optional[SlimsRewardDeliveryRdrc] = None
    reward_spouts: Optional[SlimsRewardSpoutsRdrc] = None
    stimulus_epochs: Optional[List[SlimsStimulusEpochsResult]] = []


class EcephysSessionBuilder:
    """Class to build EcephysSession objects from session run steps."""

    def __init__(self, client: SlimsClient):
        self.client = client

    def fetch_stream_modules(self, stream) -> List[SlimsStreamModule]:
        """Fetches stream modules and processes structure names."""
        stream_modules = (
            [self.client.fetch_model(SlimsDomeModuleRdrc, pk=pk)
            for pk in stream.stream_modules_pk] if stream.stream_modules_pk else []
        )

        complete_stream_modules = []
        for stream_module in stream_modules:
            primary_structure, secondary_structures = None, []

            if stream_module.primary_targeted_structure_pk:
                primary_structure = self.client.fetch_model(
                    SlimsBrainStructureRdrc,
                    pk=stream_module.primary_targeted_structure_pk
                )
                if stream_module.secondary_targeted_structures_pk:
                    secondary_structures = [
                        self.client.fetch_model(SlimsBrainStructureRdrc, pk=pk).name
                        for pk in stream_module.secondary_targeted_structures_pk
                    ]
            # print(stream_module)
            stream_module_model = SlimsStreamModule(
                **stream_module.model_dump(),
                primary_targeted_structure=primary_structure.name if primary_structure else None,
                secondary_targeted_structures=secondary_structures
            )
            complete_stream_modules.append(stream_module_model)
        return complete_stream_modules

    def fetch_streams(self, session_pk: int) -> List[SlimsStream]:
        """Fetches and completes stream information with modules."""
        streams = self.client.fetch_models(SlimsStreamsResult, mouse_session_pk=session_pk)
        complete_streams = [
            SlimsStream(
                **stream.model_dump(),
                stream_modules=self.fetch_stream_modules(stream)
            ) for stream in streams
        ]
        return complete_streams

    def fetch_reward_data(self, session) -> (Optional[SlimsRewardDeliveryRdrc], Optional[SlimsRewardSpoutsRdrc]):
        """Fetches reward delivery and spouts data."""
        reward_delivery = (
            self.client.fetch_model(SlimsRewardDeliveryRdrc, pk=session.reward_delivery_pk)
            if session.reward_delivery_pk else None
        )
        reward_spouts = (
            self.client.fetch_model(SlimsRewardSpoutsRdrc, pk=reward_delivery.reward_spouts_pk)
            if reward_delivery and reward_delivery.reward_spouts_pk else None
        )
        return reward_delivery, reward_spouts

    def _process_single_step(self, group_run_step, session_run_step) -> EcephysSession:
        """Process a single session run step into an EcephysSession."""
        session = self.client.fetch_model(SlimsMouseSessionResult, experiment_run_step_pk=session_run_step.pk)
        stimulus_epochs = self.client.fetch_models(SlimsStimulusEpochsResult, mouse_session_pk=session.pk)

        streams = self.fetch_streams(session.pk)
        reward_delivery, reward_spouts = self.fetch_reward_data(session)

        return EcephysSession(
            session_group=group_run_step,
            session_result=session,
            streams=streams or None,
            reward_delivery=reward_delivery,
            reward_spouts=reward_spouts,
            stimulus_epochs=stimulus_epochs or None,
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
        client : SlimsClient
            An instance of SlimsClient used to retrieve additional session data.
        group_run_step : SlimsGroupOfSessionsRunStep
            The group run step containing session metadata and run information.
        session_run_steps : List[SlimsMouseSessionRunStep]
            A list of individual session run steps to be processed and encapsulated.

        Returns
        -------
        List[EcephysSession]
            A list of EcephysSession objects containing the processed session data.
        """
        return [self._process_single_step(group_run_step, step) for step in session_run_steps]


    def fetch_ecephys_sessions(
        self, subject_id: str
    ) -> List[EcephysSession]:
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
        List[EcephysSession]
            A list of EcephysSession objects containing data for each run step.

        Example
        -------
        >>> from aind_slims_api import SlimsClient
        >>> client = SlimsClient()
        >>> sessions = fetch_ecephys_sessions(client=client, subject_id="000000")
        """
        ecephys_sessions_list = []
        mouse = self.client.fetch_model(SlimsMouseContent, barcode=subject_id)
        content_runs = self.client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=mouse.pk)

        for content_run in content_runs:
            try:
                # retrieves content step to find experimentrun_pk
                content_run_step = self.client.fetch_model(
                    SlimsExperimentRunStep, pk=content_run.runstep_pk
                )

                # retrieve group and mouse sessions in the experiment run
                group_run_step = self.client.fetch_models(
                    SlimsGroupOfSessionsRunStep,
                    experimentrun_pk=content_run_step.experimentrun_pk,
                )
                session_run_steps = self.client.fetch_models(
                    SlimsMouseSessionRunStep,
                    experimentrun_pk=content_run_step.experimentrun_pk,
                )
                if group_run_step and session_run_steps:
                    ecephys_sessions = self.process_session_steps(
                        group_run_step=group_run_step[0],
                        session_run_steps=session_run_steps,
                    )
                    ecephys_sessions_list.extend(ecephys_sessions)

            except SlimsRecordNotFound as e:
                logging.info(str(e))
                continue

        return ecephys_sessions_list
