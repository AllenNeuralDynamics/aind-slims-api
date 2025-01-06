"""Contains models for a histology result stored in SLIMS."""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsSampleContent(SlimsBaseModel):
    """Model for an instance of the Whole Brain ContentType

    Properties
    ----------
    barcode: str, barcode of the mouse, filterable

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(SlimsSampleContent, barcode="00000000")
    """

    barcode: str = Field(
        ...,
        serialization_alias="cntn_barCode",
        validation_alias="cntn_barCode",
    )
    mouse_barcode: Optional[str] = Field(
        None,
        serialization_alias="cntn_cf_parentBarcode",
        validation_alias="cntn_cf_parentBarcode",
    )
    pk: Optional[int] = Field(
        default=None,
        serialization_alias="cntn_pk",
        validation_alias="cntn_pk",
    )
    content_type: Optional[int] = Field(
        default=None,
        serialization_alias="cntn_fk_contentType",
        validation_alias="cntn_fk_contentType",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="cntn_createdOn",
        validation_alias="cntn_createdOn",
    )
    category_name: Optional[str] = Field(
        None, serialization_alias="category_name", validation_alias="category_name"
    )
    collection_date: Optional[datetime] = Field(
        None,
        serialization_alias="cntn_collectionDate",
        validation_alias="cntn_collectionDate",
    )
    _slims_table = "Content"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cntp_name": "Whole Brain",
    }


class SlimsReagentContent(SlimsBaseModel):
    """Model for a Reagent Content"""

    barcode: str = Field(
        ...,
        serialization_alias="cntn_barCode",
        validation_alias="cntn_barCode",
    )
    pk: Optional[int] = Field(
        default=None,
        serialization_alias="cntn_pk",
        validation_alias="cntn_pk",
    )
    content_type: Optional[int] = Field(
        default=None,
        serialization_alias="cntn_fk_contentType",
        validation_alias="cntn_fk_contentType",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="cntn_createdOn",
        validation_alias="cntn_createdOn",
    )
    lot_number: Optional[str] = Field(
        None,
        serialization_alias="cntn_cf_lotNumber",
        validation_alias="cntn_cf_lotNumber",
    )
    reagent_name: Optional[str] = Field(
        None,
        serialization_alias="cntn_cf_reagentName",
        validation_alias="cntn_cf_reagentName",
    )
    source_pk: Optional[int] = Field(
        None, serialization_alias="cntn_fk_source", validation_alias="cntn_fk_source"
    )
    _slims_table = "Content"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cntp_name": "EasyIndex",
    }


class SlimsSource(SlimsBaseModel):
    """Model for a Source"""

    pk: Optional[int] = Field(
        default=None,
        serialization_alias="sorc_pk",
        validation_alias="sorc_pk",
    )
    name: Optional[str] = Field(
        None, serialization_alias="sorc_name", validation_alias="sorc_name"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="sorc_createdOn",
        validation_alias="sorc_createdOn",
    )
    _slims_table = "Source"


class SlimsProtocolSOP(SlimsBaseModel):
    """Model for Protocols SOP"""

    pk: Optional[int] = Field(
        default=None,
        serialization_alias="stop_pk",
        validation_alias="stop_pk",
    )
    name: Optional[str] = Field(
        None, serialization_alias="stop_name", validation_alias="stop_name"
    )
    link: Optional[str] = Field(
        None, serialization_alias="stop_link", validation_alias="stop_link"
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="stop_createdOn",
        validation_alias="stop_createdOn",
    )
    _slims_table = "SOP"
