"""Contains a model for the behavior session content events, a method for
 fetching it and writing it.
"""

import logging
from typing import Any
from datetime import datetime

from pydantic import Field

from aind_slims_api.core import SlimsBaseModel, SlimsClient, SLIMSTABLES

logger = logging.getLogger()


class SlimsBehaviorSessionContentEvent(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent"""

    pk: int | None = Field(default=None, alias="cnvn_pk")
    mouse_pk: int | None = Field(
        default=None, alias="cnvn_fk_content"
    )  # used as reference to mouse
    notes: str | None = Field(default=None, alias="cnvn_cf_notes")
    task_stage: str | None = Field(default=None, alias="cnvn_cf_taskStage")
    instrument: int | None = Field(default=None, alias="cnvn_cf_fk_instrument")
    trainers: list[int] = Field(default=[], alias="cnvn_cf_fk_trainer")
    task: str | None = Field(default=None, alias="cnvn_cf_task")
    is_curriculum_suggestion: bool | None = Field(
        default=None, alias="cnvn_cf_stageIsOnCurriculum"
    )
    task_schema_version: str | None = Field(
        default=None, alias="cnvn_cf_taskSchemaVersion"
    )
    software_version: str | None = Field(default=None, alias="cnvn_cf_softwareVersion")
    date: datetime | None = Field(..., alias="cnvn_cf_scheduledDate")

    cnvn_fk_contentEventType: int = 10  # pk of Behavior Session ContentEvent

    _slims_table: SLIMSTABLES = "ContentEvent"


SlimsSingletonFetchReturn = SlimsBaseModel | dict[str, Any] | None


def _resolve_pk(
    model: SlimsSingletonFetchReturn,
    primary_key_name: str = "pk",
) -> int:
    """Utility function shared across read/write

    Notes
    -----
    - TODO: Change return type of fetch_mouse_content to match pattern in
     fetch_behavior_session_content_events, or the other way around?
    - TODO: Move to core to have better centralized control of when references
     are resolved
    """
    if isinstance(model, dict):
        logger.warning("Extracting primary key from unvalidated dict.")
        return model[primary_key_name]
    elif isinstance(model, SlimsBaseModel):
        return getattr(model, primary_key_name)
    elif model is None:
        raise ValueError(f"Cannot resolve primary key from {model}")
    else:
        raise ValueError("Unexpected type for model: %s" % type(model))


def fetch_behavior_session_content_events(
    client: SlimsClient,
    mouse: SlimsSingletonFetchReturn,
) -> tuple[list[SlimsBehaviorSessionContentEvent], list[dict[str, Any]]]:
    """Fetches behavior sessions for a mouse with labtracks id {mouse_name}

    Returns
    -------
    tuple:
        list:
            Validated SlimsBehaviorSessionContentEvent objects
        list:
            Dictionaries representations of objects that failed validation
    """
    return client.fetch_models(
        SlimsBehaviorSessionContentEvent,
        cnvn_fk_content=_resolve_pk(mouse),
        cnvt_name="Behavior Session",
        sort=["cnvn_cf_scheduledDate"],
    )


def write_behavior_session_content_events(
    client: SlimsClient,
    mouse: SlimsSingletonFetchReturn,
    instrument: SlimsSingletonFetchReturn,
    trainers: list[SlimsSingletonFetchReturn],
    *behavior_sessions: SlimsBehaviorSessionContentEvent,
) -> list[SlimsBehaviorSessionContentEvent]:
    """Writes behavior sessions for a mouse with labtracks id {mouse_name}

    Notes
    -----
    - All supplied `behavior_sessions` will have their `mouse_name` field set
     to the value supplied as `mouse_name` to this function
    """
    mouse_pk = _resolve_pk(mouse)
    logger.debug(f"Mouse pk: {mouse_pk}")
    instrument_pk = _resolve_pk(instrument)
    logger.debug(f"Instrument pk: {instrument_pk}")
    trainer_pks = [_resolve_pk(trainer) for trainer in trainers]
    logger.debug(f"Trainer pks: {trainer_pks}")
    added = []
    for behavior_session in behavior_sessions:
        updated = behavior_session.model_copy(
            update={
                "mouse_pk": mouse_pk,
                "instrument": instrument_pk,
                "trainers": trainer_pks,
            },
        )
        logger.debug(f"Resolved behavior session: {updated}")
        added.append(client.add_model(updated))

    return added
