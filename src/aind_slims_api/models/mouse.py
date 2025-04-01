"""Contains a model for the mouse content, and a method for fetching it"""

from datetime import datetime
from typing import Annotated, ClassVar, Optional

from pydantic import BeforeValidator, Field

from aind_slims_api.models.base import SlimsBaseModel
from aind_slims_api.models.utils import UnitSpec


class SlimsMouseContent(SlimsBaseModel):
    """Model for an instance of the Mouse ContentType

    Properties
    ----------
    barcode: str, barcode of the mouse, filterable

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(SlimsMouseContent, barcode="00000000")
    """

    baseline_weight_g: Annotated[float | None, UnitSpec("g")] = Field(
        ...,
        serialization_alias="cntn_cf_baselineWeight",
        validation_alias="cntn_cf_baselineWeight",
    )
    point_of_contact: Optional[str] = Field(
        ...,
        serialization_alias="cntn_cf_scientificPointOfContact",
        validation_alias="cntn_cf_scientificPointOfContact",
    )
    water_restricted: Annotated[bool, BeforeValidator(lambda x: x or False)] = Field(
        ...,
        serialization_alias="cntn_cf_waterRestricted",
        validation_alias="cntn_cf_waterRestricted",
    )
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
    status: Optional[int] = Field(
        default=28,
        serialization_alias="cntn_fk_status",
        validation_alias="cntn_fk_status",
    )
    content_type: Optional[int] = Field(
        default=5,
        serialization_alias="cntn_fk_contentType",
        validation_alias="cntn_fk_contentType",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="cntn_createdOn",
        validation_alias="cntn_createdOn",
    )
    _slims_table = "Content"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cntp_name": "Mouse",
    }

    # TODO: Include other helpful fields (genotype, gender...)

    # pk: callable
    # cntn_fk_category: SlimsColumn
    # cntn_fk_contentType: SlimsColumn
    # cntn_barCode: SlimsColumn
    # cntn_id: SlimsColumn
    # cntn_cf_contactPerson: SlimsColumn
    # cntn_status: SlimsColumn
    # cntn_fk_status: SlimsColumn
    # cntn_fk_user: SlimsColumn
    # cntn_cf_fk_fundingCode: SlimsColumn
    # cntn_cf_genotype: SlimsColumn
    # cntn_cf_labtracksId: SlimsColumn
    # cntn_cf_parentBarcode: SlimsColumn
