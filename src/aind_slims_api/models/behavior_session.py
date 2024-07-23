"""Contains a model for the behavior session content events, a method for
 fetching it and writing it.
"""

import logging
from datetime import datetime
from typing import ClassVar

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel

logger = logging.getLogger()


class SlimsBehaviorSession(SlimsBaseModel):
    """Model for an instance of the Behavior Session ContentEvent

    Examples
    --------
    Read a session.

    >>> from datetime import datetime
    >>> from aind_slims_api import SlimsClient
    >>> from aind_slims_api.models import SlimsMouseContent
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(SlimsMouseContent, barcode="00000000")
    >>> behavior_sessions = client.fetch_models(SlimsBehaviorSession,
    ...  mouse_pk=mouse.pk, sort=["date"])
    >>> curriculum_attachments = client.fetch_attachments(behavior_sessions[0])

    Write a new session.
    >>> from aind_slims_api.models import SlimsInstrument, SlimsUser
    >>> trainer = client.fetch_model(SlimsUser, username="LKim")
    >>> instrument = client.fetch_model(SlimsInstrument, name="323_EPHYS1_OPTO")
    >>> added = client.add_model(
    ...  SlimsBehaviorSession(
    ...      cnvn_fk_content=mouse.pk,
    ...      cnvn_cf_fk_instrument=instrument.pk,
    ...      cnvn_cf_fk_trainer=[trainer.pk],
    ...      cnvn_cf_notes="notes",
    ...      cnvn_cf_taskStage="stage",
    ...      cnvn_cf_task="task",
    ...      cnvn_cf_taskSchemaVersion="0.0.1",
    ...      cnvn_cf_stageIsOnCurriculum=True,
    ...      cnvn_cf_scheduledDate=datetime(2021, 1, 2),
    ...  )
    ... )

    Add a curriculum attachment to the session (Attachment content isn't
     available immediately.)
    >>> import json
    >>> attachment_pk = client.add_attachment_content(
    ...  added,
    ...  "curriculum",
    ...  json.dumps({"curriculum_key": "curriculum_value"}),
    ... )
    """

    pk: int | None = Field(default=None, alias="cnvn_pk")
    mouse_pk: int | None = Field(
        default=None,
        alias="cnvn_fk_content",
        description=(
            "The primary key of the mouse associated with this behavior session."
        ),
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
    date: datetime | None = Field(default=None, alias="cnvn_cf_scheduledDate")
    cnvn_fk_contentEventType: int = 10  # pk of Behavior Session ContentEvent
    _slims_table = "ContentEvent"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cnvt_name": "Behavior Session",
    }
