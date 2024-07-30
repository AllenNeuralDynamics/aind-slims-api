"""Contains a model for a unit"""

from datetime import datetime
from typing import Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsUnit(SlimsBaseModel):
    """Model for unit information in SLIMS"""

    name: str = Field(
        ...,
        serialization_alias="unit_name",
        validation_alias="unit_name",
    )
    abbreviation: Optional[str] = Field(
        "",
        serialization_alias="unit_abbreviation",
        validation_alias="unit_abbreviation",
    )
    pk: int = Field(
        ...,
        serialization_alias="unit_pk",
        validation_alias="unit_pk",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="unit_createdOn",
        validation_alias="unit_createdOn",
    )
    _slims_table = "Unit"
