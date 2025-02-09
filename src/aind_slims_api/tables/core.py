from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Type

from pydantic import BaseModel, Field
from slims.internal import Record
from sqlmodel import SQLModel


class SlimsColumnDataType(str, Enum):
    """
    This may need to be updated. Can be replaced if these values are accessible
    from the slims python SDK
    """

    BOOLEAN = "BOOLEAN"
    DATE = "DATE"
    ENUM = "ENUM"
    FLOAT = "FLOAT"
    FOREIGN_KEY = "FOREIGN_KEY"
    INTEGER = "INTEGER"
    MULTIPLE_ENUM = "MULTIPLE_ENUM"
    MULTIPLE_FOREIGN_KEY = "MULTIPLE_FOREIGN_KEY"
    NA = "NA"
    QUANTITY = "QUANTITY"
    STRING = "STRING"


class Quantity(BaseModel):
    """
    Quantity appears to be a custom type that contains a value and a unit.
    """

    value: Optional[float] = Field(default=None)
    unit: Optional[str] = Field(default=None)


def get_value_or_none(record: Record, field_name: str) -> Optional[Any]:
    """
    Get a value for a record attribute. If the record does not have the attribute.
    then return None. This is useful because a Record object does not always
    contain all the attributes for the table it is pulled from.
    Parameters
    ----------
    record : Record
    field_name : str

    Returns
    -------
    Optional[Any]

    """
    if hasattr(record, field_name):
        obj_field = getattr(record, field_name)
        return getattr(obj_field, "value", None)
    else:
        return None


def records_to_models(records: List[Record], model: Type[SQLModel]) -> List[SQLModel]:
    models = []
    for record in records:
        model_dict = dict()
        for col in record.json_entity["columns"]:
            data_type = col.get("datatype")
            name = col.get("name")
            value = col.get("value")
            match data_type:
                case (
                    SlimsColumnDataType.BOOLEAN
                    | SlimsColumnDataType.ENUM
                    | SlimsColumnDataType.FLOAT
                    | SlimsColumnDataType.FOREIGN_KEY
                    | SlimsColumnDataType.INTEGER
                    | SlimsColumnDataType.MULTIPLE_FOREIGN_KEY
                    | SlimsColumnDataType.MULTIPLE_ENUM
                    | SlimsColumnDataType.STRING
                ):
                    model_dict[name] = value
                case SlimsColumnDataType.DATE:
                    if isinstance(value, int):
                        dt = datetime.fromtimestamp(value / 1000)
                    else:
                        dt = None
                    model_dict[name] = dt
                case SlimsColumnDataType.QUANTITY:
                    unit = col.get("unit")
                    quantity = Quantity(unit=unit, value=value)
                    model_dict[name] = quantity
                case _:
                    pass
        constructed_model = model.model_validate(model_dict)
        models.append(constructed_model)
    return models
