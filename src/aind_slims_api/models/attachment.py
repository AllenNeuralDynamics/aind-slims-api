"""Model for a record in the Attachment table in SLIMS."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsAttachment(SlimsBaseModel):
    """Model for a record in the Attachment table in SLIMS.

    Examples
    --------
    >>> from aind_slims_api import SlimsClient
    >>> from aind_slims_api import models
    >>> client = SlimsClient()
    >>> rig_metadata_attachment = client.fetch_model(
    ...  models.SlimsAttachment,
    ...  name="rig323_EPHYS1_OPTO_2024-02-12.json"
    ... )
    >>> rig_metadata = client.fetch_attachment_content(
    ...  rig_metadata_attachment
    ... ).json()
    >>> rig_metadata["rig_id"]
    '323_EPHYS1_OPTO_2024-02-12'
    """

    pk: int = Field(
        ...,
        serialization_alias="attm_pk",
        validation_alias="attm_pk",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="attm_createdOn",
        validation_alias="attm_createdOn",
    )
    name: str = Field(
        ...,
        serialization_alias="attm_name",
        validation_alias="attm_name",
    )
    _slims_table = "Attachment"
