"""
Module defining operations to build EcephysSession.
"""

from typing import List, Optional
from pydantic import BaseModel
from aind_slims_api import SlimsClient
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
)


class EcephysSession(BaseModel):
    """
    Pydantic model encapsulating all session-related responses.
    """
    session_group: Optional[SlimsExperimentRunStep]
    session_result: Optional[SlimsMouseSessionResult]
    streams: Optional[List[SlimsStreamsResult]] = None
    stream_modules: Optional[List[SlimsDomeModuleRdrc]] = None
    reward_delivery: Optional[SlimsRewardDeliveryRdrc] = None
    reward_spouts: Optional[List[SlimsRewardSpoutsRdrc]] = None
    stimulus_epochs: Optional[List[SlimsStimulusEpochsResult]] = None



class SlimsEcephysSession:
    """
    Class for fetching and encapsulating EcephysSession data from SLIMS.
    """

    def __init__(self, subject_id: str, slims_client: Optional[SlimsClient] = None):
        """
        Initializes the handler with the subject ID and optional SLIMS client.
        """
        self.subject_id = subject_id
        self.client = slims_client or SlimsClient()

    def fetch_ecephys_session(self, run_steps: List[SlimsExperimentRunStep]) -> List[EcephysSession]:
        """
        Fetch all data related to a single ecephys session and return a list of EcephysSession objects.
        """
        session_groups = [step for step in run_steps if step.name == "Group of Sessions"]
        ecephys_sessions = []

        for step in run_steps:
            if step.name == "Mouse Session":
                sessions = self.client.fetch_models(SlimsMouseSessionResult, experiment_run_step_pk=step.pk)

                for session in sessions:
                    streams = self.client.fetch_models(SlimsStreamsResult, mouse_session_pk=session.pk)
                    stream_modules = []
                    reward_delivery = None
                    reward_spouts = None

                    if streams:
                        for stream in streams:
                            stream_modules.extend(
                                self.client.fetch_models(SlimsDomeModuleRdrc, pk=stream_module_pk)
                                for stream_module_pk in stream.stream_modules_pk
                            )

                    if session.reward_delivery_pk:
                        reward_delivery = self.client.fetch_model(SlimsRewardDeliveryRdrc, pk=session.reward_delivery_pk)
                        if reward_delivery.reward_spouts_pk:
                            reward_spouts = [
                                self.client.fetch_model(SlimsRewardSpoutsRdrc, pk=pk)
                                for pk in reward_delivery.reward_spouts_pk
                            ]

                    stimulus_epochs = self.client.fetch_models(
                        SlimsStimulusEpochsResult, experiment_run_step_pk=step.pk
                    )

                    ecephys_session = EcephysSession(
                        session_group=session_groups[0] if session_groups else None,
                        session_result=session,
                        streams=streams or None,
                        stream_modules=stream_modules or None,
                        reward_delivery=reward_delivery,
                        reward_spouts=reward_spouts,
                        stimulus_epochs=stimulus_epochs or None,
                    )
                    ecephys_sessions.append(ecephys_session)

        return ecephys_sessions

    def process_run_steps(self) -> List[EcephysSession]:
        """
        Process all run steps for a given mouse and return a list of EcephysSession objects.
        """
        ecephys_sessions_list = []
        mouse = self.client.fetch_model(SlimsMouseContent, barcode=self.subject_id)
        content_runs = self.client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=mouse.pk)

        for content_run in content_runs:
            try:
                content_run_step = self.client.fetch_model(SlimsExperimentRunStep, pk=content_run.runstep_pk)
                run_steps = self.client.fetch_models(SlimsExperimentRunStep, experimentrun_pk=content_run_step.experimentrun_pk)

                ecephys_sessions = self.fetch_ecephys_session(run_steps=run_steps)
                ecephys_sessions_list.extend(ecephys_sessions)

            except Exception as e:
                print(f"Error processing run step {content_run.runstep_pk}: {e}")

        return ecephys_sessions_list
