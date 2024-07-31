"""Contains a model for the behavior session content events, a method for
 fetching it and writing it.
"""

import logging
from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel

logger = logging.getLogger()


class SlimsBehaviorSession(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent

    Examples
    --------
    >>> from datetime import datetime
    >>> from aind_slims_api import SlimsClient
    >>> from aind_slims_api import models
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(models.SlimsMouseContent, barcode="00000000")

    ### Read
    >>> behavior_sessions = client.fetch_models(SlimsBehaviorSession,
    ...  mouse_pk=mouse.pk, sort=["date"])
    >>> curriculum_attachments = client.fetch_attachments(behavior_sessions[0])

    ### Write
    >>> trainer = client.fetch_model(models.SlimsUser, username="LKim")
    >>> instrument = client.fetch_model(models.SlimsInstrument, name="323_EPHYS1_OPTO")
    >>> added = client.add_model(
    ...  SlimsBehaviorSession(
    ...      mouse_pk=mouse.pk,
    ...      instrument_pk=instrument.pk,
    ...      trainer_pks=[trainer.pk],
    ...      notes="notes",
    ...      task_stage="stage",
    ...      task="task",
    ...      task_schema_version="0.0.1",
    ...      is_curriculum_suggestion=True,
    ...      date=datetime(2021, 1, 2),
    ...  )
    ... )

    ### Add a curriculum attachment
    Attachment content isn't available immediately.
    >>> import json
    >>> attachment_pk = client.add_attachment_content(
    ...  added,
    ...  "curriculum",
    ...  json.dumps({"curriculum_key": "curriculum_value"}),
    ... )

    Properties
    ----------
    mouse_pk : Optional[int]
        The primary key of the mouse associated with this behavior session.
    instrument_pk : Optional[int]
        The primary key of the instrument associated with this behavior session.
    trainer_pks : Optional[list[int]]
        The primary keys of the trainers associated with this behavior session.
    task : Optional[str]
        Name of the task associated with the session.
    task_stage : Optional[str]
        Name of the stage associated with the session.
    task_schema_version : Optional[str]
        Version of the task schema.
    is_curriculum_suggestion : Optional[bool]
        Whether the session is a curriculum suggestion.
    date : Optional[datetime]
        Date of the suggestion.
    notes : Optional[str]
        Notes about the session.
    """

    pk: Optional[int] = Field(
        default=None,
        serialization_alias="cnvn_pk",
        validation_alias="cnvn_pk",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="cnvn_createdOn",
        validation_alias="cnvn_createdOn",
    )
    mouse_pk: Optional[int] = Field(
        default=None,
        serialization_alias="cnvn_fk_content",
        validation_alias="cnvn_fk_content",
        description=(
            "The primary key of the mouse associated with this behavior session."
        ),
    )  # used as reference to mouse
    notes: Optional[str] = Field(
        default=None,
        serialization_alias="cnvn_cf_notes",
        validation_alias="cnvn_cf_notes",
    )
    task_stage: Optional[str] = Field(
        default=None,
        serialization_alias="cnvn_cf_taskStage",
        validation_alias="cnvn_cf_taskStage",
    )
    instrument_pk: Optional[int] = Field(
        default=None,
        serialization_alias="cnvn_fk_instrument",
        validation_alias="cnvn_fk_instrument",
    )
    trainer_pks: Optional[list[int]] = Field(
        default=[],
        serialization_alias="cnvn_cf_fk_trainer",
        validation_alias="cnvn_cf_fk_trainer",
    )
    task: Optional[str] = Field(
        default=None,
        serialization_alias="cnvn_cf_task",
        validation_alias="cnvn_cf_task",
    )
    is_curriculum_suggestion: Optional[bool] = Field(
        default=None,
        serialization_alias="cnvn_cf_stageIsOnCurriculum",
        validation_alias="cnvn_cf_stageIsOnCurriculum",
    )
    task_schema_version: Optional[str] = Field(
        default=None,
        serialization_alias="cnvn_cf_taskSchemaVersion",
        validation_alias="cnvn_cf_taskSchemaVersion",
    )
    software_version: Optional[str] = Field(
        default=None,
        serialization_alias="cnvn_cf_softwareVersion",
        validation_alias="cnvn_cf_softwareVersion",
    )
    date: Optional[datetime] = Field(
        default=None,
        serialization_alias="cnvn_cf_scheduledDate",
        validation_alias="cnvn_cf_scheduledDate",
    )
    cnvn_fk_contentEventType: int = 10  # pk of Behavior Session ContentEvent
    _slims_table = "ContentEvent"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cnvt_name": "Behavior Session",
    }
