"""Module defining operations to build EcephysSession"""

from typing import List, Optional
from pydantic import BaseModel
from aind_slims_api import SlimsClient
from aind_slims_api.models.mouse import SlimsMouseContent
from aind_slims_api.models.ecephys_session import (
     SlimsMouseSessionResult,
     SlimsStreamsResult,
     SlimsStimulusEpochsResult,
     SlimsExperimentRunStepContent,
     SlimsExperimentRunStep
)

# model to encapsulate all session-related data
class EcephysSession(BaseModel):
    group_steps: SlimsExperimentRunStep
    session_result: SlimsMouseSessionResult
    streams: List[SlimsStreamsResult]
    stimulus_epochs: List[SlimsStimulusEpochsResult]

class SlimsEcephysSessionHandler:
    """"""
    def __init__(self, subject_id: str, slims_client=None):
        """"""
        self.subject_id = subject_id
        self.client = slims_client or SlimsClient()
        self.mouse = self.client.fetch_model(SlimsMouseContent, barcode=subject_id)

    def fetch_ecephys_session(self, run_steps):
        """Fetch all the data related to a single ecephys session and return a session object."""

        # Fetch and filter 'Group of Sessions' steps
        group_steps = [step for step in run_steps if step.name == "Group of Sessions"]

        # Initialize the session data object
        ecephys_sessions = []

        # Find 'Mouse Session' steps
        for step in run_steps:
            if step.name == "Mouse Session":
                # Fetch the mouse sessions related to this run step
                sessions = self.client.fetch_models(SlimsMouseSessionResult, experiment_run_step_pk=step.pk)

                for session in sessions:
                    # Fetch related streams and stimulus epochs
                    streams = self.client.fetch_models(SlimsStreamsResult, mouse_session_pk=session.pk)
                    # TODO: fetch stream modules
                    stimulus_epochs = self.client.fetch_models(SlimsStimulusEpochsResult, experiment_run_step_pk=step.pk)

                    # Combine all data into a single EcephysSession object
                    ecephys_session = EcephysSession.model_construct(
                        group_steps=group_steps,
                        session_result=session,
                        streams=streams if streams else None,
                        stimulus_epochs=[epoch for epoch in stimulus_epochs] if stimulus_epochs else None
                    )

                    # Append the session to the list
                    ecephys_sessions.append(ecephys_session)

        return ecephys_sessions


    def process_run_steps(self):
        """Process all run steps for a given mouse and return a list of EcephysSession objects."""
        ecephys_sessions_list = []

        # Fetch all content runs for the given mouse
        content_runs = self.client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=self.mouse.pk)

        # Loop through each content run
        for content_run in content_runs:
            try:
                # Fetch the associated experiment run step by runstep_pk
                content_run_step = self.client.fetch_model(SlimsExperimentRunStep, pk=content_run.runstep_pk)

                # Fetch all run steps for the experiment run
                run_steps = self.client.fetch_models(SlimsExperimentRunStep, experimentrun_pk=content_run_step.experimentrun_pk)

                # Fetch ecephys sessions for the current content run step
                ecephys_sessions = self.fetch_ecephys_session(run_steps=run_steps)

                # Append the fetched sessions to the list
                ecephys_sessions_list.extend(ecephys_sessions)

            except Exception as e:
                print(f"Error processing run step {content_run.runstep_pk}: {e}")

        return ecephys_sessions_list

