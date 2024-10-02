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
    SlimsMouseSessionRunStep,
)

logger = logging.getLogger(__name__)


class EcephysSession(BaseModel):
    """
    Pydantic model encapsulating all session-related responses.
    """

    session_group: Optional[SlimsExperimentRunStep]
    session_result: Optional[SlimsMouseSessionResult]
    streams: Optional[List[SlimsStreamsResult]] = []
    stream_modules: Optional[List[SlimsDomeModuleRdrc]] = []
    reward_delivery: Optional[SlimsRewardDeliveryRdrc] = None
    reward_spouts: Optional[SlimsRewardSpoutsRdrc] = None
    stimulus_epochs: Optional[List[SlimsStimulusEpochsResult]] = []


class SlimsEcephysSessionOperator:
    """
    Class for fetching and encapsulating EcephysSession data from SLIMS.
    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> from aind_slims_api.operations.ecephys_session import SlimsEcephysSessionOperator
    >>> client = SlimsClient()
    >>> operator = SlimsEcephysSessionOperator(slims_client=client)
    >>> operator.fetch_sessions(subject_id="000000")
    """

    def __init__(self, slims_client: Optional[SlimsClient] = None):
        """
        Initializes the handler with the subject ID and optional SLIMS client.
        """
        self.client = slims_client or SlimsClient()

    def _process_session_steps(
        self,
        group_run_step: SlimsGroupOfSessionsRunStep,
        session_run_steps: List[SlimsMouseSessionRunStep],
    ) -> List[EcephysSession]:
        """
        Fetch all data related to a single ecephys session
        and return a list of EcephysSession objects.
        """
        ecephys_sessions = []

        for step in session_run_steps:
            # retrieve session, streams, and epochs from Results table
            session = self.client.fetch_model(
                SlimsMouseSessionResult, experiment_run_step_pk=step.pk
            )
            streams = self.client.fetch_models(
                SlimsStreamsResult, mouse_session_pk=session.pk
            )
            stimulus_epochs = self.client.fetch_models(
                SlimsStimulusEpochsResult, mouse_session_pk=session.pk
            )

            # retrieve modules and reward info from ReferenceDataRecord table
            stream_modules = [
                self.client.fetch_model(SlimsDomeModuleRdrc, pk=stream_module_pk)
                for stream in streams
                if stream.stream_modules_pk
                for stream_module_pk in stream.stream_modules_pk
            ]

            reward_delivery = (
                self.client.fetch_model(
                    SlimsRewardDeliveryRdrc, pk=session.reward_delivery_pk
                )
                if session.reward_delivery_pk
                else None
            )

            reward_spouts = (
                self.client.fetch_model(
                    SlimsRewardSpoutsRdrc, pk=reward_delivery.reward_spouts_pk
                )
                if reward_delivery and reward_delivery.reward_spouts_pk
                else None
            )

            # encapsulate all info for a single session
            ecephys_session = EcephysSession(
                session_group=group_run_step,
                session_result=session,
                streams=streams or None,
                stream_modules=stream_modules or None,
                reward_delivery=reward_delivery,
                reward_spouts=reward_spouts,
                stimulus_epochs=stimulus_epochs or None,
            )
            ecephys_sessions.append(ecephys_session)

        return ecephys_sessions

    def fetch_sessions(self, subject_id: str) -> List[EcephysSession]:
        """
        Process all run steps for a given mouse
         and return a list of EcephysSession objects.
        """
        ecephys_sessions_list = []
        mouse = self.client.fetch_model(SlimsMouseContent, barcode=subject_id)
        content_runs = self.client.fetch_models(
            SlimsExperimentRunStepContent, mouse_pk=mouse.pk
        )

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
                    ecephys_sessions = self._process_session_steps(
                        group_run_step=group_run_step[0],
                        session_run_steps=session_run_steps,
                    )
                    ecephys_sessions_list.extend(ecephys_sessions)

            except SlimsRecordNotFound as e:
                logging.info(str(e))
                continue

        return ecephys_sessions_list
