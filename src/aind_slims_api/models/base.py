"""Base model for SLIMS records abstraction.
"""

import logging
from datetime import datetime
from typing import ClassVar, Optional

from pydantic import BaseModel, ValidationInfo, field_serializer, field_validator
from slims.internal import Column as SlimsColumn

from aind_slims_api.models.utils import _find_unit_spec
from aind_slims_api.types import SLIMSTABLES

logger = logging.getLogger(__name__)


class SlimsBaseModel(
    BaseModel,
    from_attributes=True,
    validate_assignment=True,
):
    """Pydantic model to represent a SLIMS record.
    Subclass with fields matching those in the SLIMS record.

    For Quantities, specify acceptable units like so:

        class MyModel(SlimsBaseModel):
            myfield: Annotated[float | None, UnitSpec("g","kg")]

        Quantities will be serialized using the first unit passed

    Datetime fields will be serialized to an integer ms timestamp
    """

    pk: Optional[int] = None
    json_entity: Optional[dict] = None
    _slims_table: ClassVar[SLIMSTABLES]
    # base filters for model fetch
    _base_fetch_filters: ClassVar[dict[str, str]] = {}

    @field_validator("*", mode="before")
    def _validate(cls, value, info: ValidationInfo):
        """Validates a field, accounts for Quantities"""
        if isinstance(value, SlimsColumn):
            if value.datatype == "QUANTITY":
                unit_spec = _find_unit_spec(cls.model_fields[info.field_name])
                if unit_spec is None:
                    msg = (
                        f'Quantity field "{info.field_name}"'
                        "must be annotated with a UnitSpec"
                    )
                    raise TypeError(msg)
                if value.unit not in unit_spec.units:
                    msg = (
                        f'Unexpected unit "{value.unit}" for field '
                        f"{info.field_name}, Expected {unit_spec.units}"
                    )
                    raise ValueError(msg)
            return value.value
        else:
            return value

    @field_serializer("*")
    def _serialize(self, field, info):
        """Serialize a field, accounts for Quantities and datetime"""
        unit_spec = _find_unit_spec(self.model_fields[info.field_name])
        if unit_spec and field is not None:
            quantity = {
                "amount": field,
                "unit_display": unit_spec.preferred_unit,
            }
            return quantity
        elif isinstance(field, datetime):
            return int(field.timestamp() * 10**3)
        else:
            return field

    # TODO: Add links - need Record.json_entity['links']['self']
    # TODO: Add Table - need Record.json_entity['tableName']
