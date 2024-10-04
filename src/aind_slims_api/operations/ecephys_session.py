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

    session_group: SlimsExperimentRunStep
    session_result: Optional[SlimsMouseSessionResult]
    streams: Optional[List[SlimsStreamsResult]] = []
    stream_modules: Optional[List[SlimsDomeModuleRdrc]] = []
    reward_delivery: Optional[SlimsRewardDeliveryRdrc] = None
    reward_spouts: Optional[SlimsRewardSpoutsRdrc] = None
    stimulus_epochs: Optional[List[SlimsStimulusEpochsResult]] = []


def _process_session_steps(
    client: SlimsClient,
    group_run_step: SlimsGroupOfSessionsRunStep,
    session_run_steps: List[SlimsMouseSessionRunStep],
) -> List[EcephysSession]:
    """
    Process session run steps and encapsulate related data into EcephysSession objects.
    Iterates through each run step in the provided session run steps,
    gathers the necessary data, and creates a list of EcephysSession objects.

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
    ecephys_sessions = []

    for step in session_run_steps:
        # retrieve session, streams, and epochs from Results table
        session = client.fetch_model(
            SlimsMouseSessionResult, experiment_run_step_pk=step.pk
        )
        streams = client.fetch_models(SlimsStreamsResult, mouse_session_pk=session.pk)
        stimulus_epochs = client.fetch_models(
            SlimsStimulusEpochsResult, mouse_session_pk=session.pk
        )

        # retrieve modules and reward info from ReferenceDataRecord table
        stream_modules = [
            client.fetch_model(SlimsDomeModuleRdrc, pk=stream_module_pk)
            for stream in streams
            if stream.stream_modules_pk
            for stream_module_pk in stream.stream_modules_pk
        ]

        reward_delivery = (
            client.fetch_model(SlimsRewardDeliveryRdrc, pk=session.reward_delivery_pk)
            if session.reward_delivery_pk
            else None
        )

        reward_spouts = (
            client.fetch_model(
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


def fetch_ecephys_sessions(
    client: SlimsClient, subject_id: str
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
    mouse = client.fetch_model(SlimsMouseContent, barcode=subject_id)
    content_runs = client.fetch_models(SlimsExperimentRunStepContent, mouse_pk=mouse.pk)

    for content_run in content_runs:
        try:
            # retrieves content step to find experimentrun_pk
            content_run_step = client.fetch_model(
                SlimsExperimentRunStep, pk=content_run.runstep_pk
            )

            # retrieve group and mouse sessions in the experiment run
            group_run_step = client.fetch_models(
                SlimsGroupOfSessionsRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk,
            )
            session_run_steps = client.fetch_models(
                SlimsMouseSessionRunStep,
                experimentrun_pk=content_run_step.experimentrun_pk,
            )
            if group_run_step and session_run_steps:
                ecephys_sessions = _process_session_steps(
                    client=client,
                    group_run_step=group_run_step[0],
                    session_run_steps=session_run_steps,
                )
                ecephys_sessions_list.extend(ecephys_sessions)

        except SlimsRecordNotFound as e:
            logging.info(str(e))
            continue

    return ecephys_sessions_list
