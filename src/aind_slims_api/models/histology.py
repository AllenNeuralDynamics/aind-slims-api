"""Contains models for a histology result stored in SLIMS."""

from datetime import datetime
from typing import Any, ClassVar, Optional

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
    reagent_ref_pk: Optional[int] = Field(
        None,
        serialization_alias="cntn_cf_fk_reagentCatalogNumber",
        validation_alias="cntn_cf_fk_reagentCatalogNumber",
    )
    source_pk: Optional[int] = Field(
        None, serialization_alias="cntn_fk_source", validation_alias="cntn_fk_source"
    )
    _slims_table = "Content"


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


class SlimsReagentDetailsRdrc(SlimsBaseModel):
    """Model for a Reagent Catalog Reference Data Record"""

    pk: Optional[int] = Field(
        None, serialization_alias="rdrc_pk", validation_alias="rdrc_pk"
    )
    name: Optional[str] = Field(
        None, serialization_alias="rdrc_name", validation_alias="rdrc_name"
    )
    manufacturer_pk: Optional[int] = Field(
        None,
        serialization_alias="rdrc_cf_fk_manufacturer",
        validation_alias="rdrc_cf_fk_manufacturer",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, Any]] = {
        "rdty_name": [
            "External reagent details",
            "Reagent Details",
            "Internally Produced Reagent Details",
        ]
    }


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
