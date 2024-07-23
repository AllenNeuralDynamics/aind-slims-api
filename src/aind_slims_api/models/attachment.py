"""Model for a record in the Attachment table in SLIMS."""

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsAttachment(SlimsBaseModel):
    """Model for a record in the Attachment table in SLIMS.

    Examples
    --------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    >>> rig_metadata_attachment = client.fetch_model(
    ...  SlimsAttachment,
    ...  name="rig323_EPHYS1_OPTO_2024-02-12.json"
    ... )
    >>> rig_metadata = client.fetch_attachment_content(
    ...  rig_metadata_attachment
    ... ).json()
    >>> rig_metadata["rig_id"]
    '323_EPHYS1_OPTO_2024-02-12'
    """

    pk: int = Field(..., alias="attm_pk")
    name: str = Field(alias="attm_name")
    _slims_table = "Attachment"
