"""Models for the metadata stored in SLIMS."""

from pydantic import Field
from typing import Optional
from aind_slims_api.models.base import SlimsBaseModel


class SlimsMetadataReference(SlimsBaseModel):
    """Model for an instance of the metadata reference in SLIMS. Metadata
     content is added to metadata references in the form of attachments.

    Examples
    --------
    >>> from aind_slims_api import SlimsClient
    >>> from aind_slims_api import models
    >>> client = SlimsClient()

    ### Read
    >>> metadata_reference = client.fetch_model(
    ...  models.SlimsMetadataReference,
    ...  name="323_EPHYS1_OPTO_20240212"
    ... )
    >>> attachments = client.fetch_attachments(metadata_reference)
    >>> metadata = client.fetch_attachment_content(attachments[0])
    >>> metadata.json()["rig_id"]
    '323_EPHYS1_OPTO_2024-02-12'

    ### Write
    >>> import json
    >>> attachment_pk = client.add_attachment_content(
    ...  metadata_reference,
    ...  "test_metadata_attachment_name",
    ...  json.dumps({"rig_id": "323_EPHYS1_OPTO_2024-02-12"})
    ... )
    """

    name: str = Field(
        ...,
        serialization_alias="rdrc_name",
        validation_alias="rdrc_name",
    )
    pk: Optional[int] = Field(
        None,
        serialization_alias="rdrc_pk",
        validation_alias="rdrc_pk",
    )
    _slims_table = "ReferenceDataRecord"
