"""Contains a model for the mouse content, and a method for fetching it"""

from datetime import datetime
from typing import Annotated, ClassVar, Literal, Optional

from pydantic import BeforeValidator, Field

from aind_slims_api.models.base import SlimsBaseModel
from aind_slims_api.models.utils import UnitSpec

SEX = Literal["Male", "Female"]


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

    x_offset: Optional[float] = Field(
        default=None,
        serialization_alias="cntn_cf_mouseXOffset",
        validation_alias="cntn_cf_mouseXOffset",
    )

    y_offset: Optional[float] = Field(
        default=None,
        serialization_alias="cntn_cf_mouseYOffset",
        validation_alias="cntn_cf_mouseYOffset",
    )

    z_offset: Optional[float] = Field(
        default=None,
        serialization_alias="cntn_cf_mouseZOffset",
        validation_alias="cntn_cf_mouseZOffset",
    )

    name: Optional[str] = Field(
        default=None,
        serialization_alias="cntn_id",
        validation_alias="cntn_id",
    )

    breeding_group: Optional[str] = Field(
        default=None,
        serialization_alias="cntn_cf_labtracksGroup",
        validation_alias="cntn_cf_labtracksGroup",
    )

    full_genotype: Optional[str] = Field(
        default=None,
        serialization_alias="cntn_cf_genotype",
        validation_alias="cntn_cf_genotype",
    )

    sex: Optional[SEX] = Field(
        default=None,
        serialization_alias="cntn_cf_sex",
        validation_alias="cntn_cf_sex",
    )

    date_of_birth: Optional[datetime] = Field(
        default=None,
        serialization_alias="cntn_cf_dateOfBirth",
        validation_alias="cntn_cf_dateOfBirth",
    )

    project_id: Optional[int] = Field(
        default=None,
        serialization_alias="cntn_cf_fk_projectId",
        validation_alias="cntn_cf_fk_projectId",
    )

    contact_person: Optional[str] = Field(
        default=None,
        serialization_alias="cntn_cf_contactPerson",
        validation_alias="cntn_cf_contactPerson",
    )

    parent_barcode: Optional[str] = Field(
        default=None,
        serialization_alias="cntn_cf_parentBarcode",
        validation_alias="cntn_cf_parentBarcode",
    )

    parent_name: Optional[str] = Field(
        default=None,
        serialization_alias="cntn_cf_parentName",
        validation_alias="cntn_cf_parentName",
    )

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

    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="cntn_createdOn",
        validation_alias="cntn_createdOn",
    )
    type_fk: Optional[int] = Field(
        None,
        serialization_alias="cntn_fk_contentType",
        validation_alias="cntn_fk_contentType",
        json_schema_extra={"type_table": "ContentType"}
    )

    _slims_table = "Content"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cntp_name": "Mouse",
    }

    # pk: callable
    # cntn_fk_category: SlimsColumn
    # cntn_fk_contentType: SlimsColumn
    # cntn_fk_user: SlimsColumn
