"""Contains a model for the mouse content, and a method for fetching it"""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsMouseLickspoutOffsets(SlimsBaseModel):
    """Model for an instance of the Mouse Lickspout Offsets data table

    Properties
    ----------
    mouse_name: str, barcode of the mouse, filterable
    x_offset: x offset of lickspout
    y_offset: y offset of lickspout
    z_offset: z offset of lickspout

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(SlimsMouseLickspoutOffsets, barcode="00000000")
    """

    mouse_id: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_fk_mouseID",
        validation_alias="rdrc_cf_fk_mouseID",
    )
    barcode: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_name",
        validation_alias="rdrc_name",
    )

    x_offset: Optional[float] = Field(
        default=None,
        serialization_alias="rdrc_cf_offsetX",
        validation_alias="rdrc_cf_offsetX",
    )

    y_offset: Optional[float] = Field(
        default=None,
        serialization_alias="rdrc_cf_offsetY",
        validation_alias="rdrc_cf_offsetY",
    )

    z_offset: Optional[float] = Field(
        default=None,
        serialization_alias="rdrc_cf_offsetZ",
        validation_alias="rdrc_cf_offsetZ",
    )

    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )

    pk: Optional[int] = Field(
        default=None,
        serialization_alias="rdrc_pk",
        validation_alias="rdrc_pk",
    )

    type_fk: Optional[int] = Field(
        None,
        serialization_alias="rdrc_fk_referenceDataType",
        validation_alias="rdrc_fk_referenceDataType",
        json_schema_extra={"type_table": "ReferenceDataType"}
    )

    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "Mouse lickspout offsets",
    }
