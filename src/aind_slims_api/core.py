from datetime import timezone as tz
import datetime
from datetime import datetime
from enum import Enum
from functools import lru_cache
import os
import json
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from pydantic import (
    BaseModel,
    BeforeValidator,
    ValidationError,
    ValidationInfo,
    conlist,
    field_serializer,
    field_validator,
    model_validator,
)
from pydantic.fields import FieldInfo
import requests
from requests.auth import HTTPBasicAuth
import logging
from typing import Annotated, Any, Self, Union, Literal, Optional
import math

from slims.slims import Slims, _SlimsApiException
from slims.internal import (
    Column as SlimsColumn,
    Record as SlimsRecord,
)
from slims.criteria import Criterion, conjunction, equals

from aind_slims_api import config

logger = logging.getLogger()

# List of slims tables manually accessed, there are many more
SLIMSTABLES = Literal[
    "Project",
    "Content",
    "ContentEvent",
    "Unit",
    "Result",
    "Test",
    "User",
    "Groups",
]


class UnitSpec:
    units: list[str]
    preferred_unit: str = None

    def __init__(self, *args, preferred_unit=None):
        self.units = args
        if len(self.units) == 0:
            raise ValueError("One or more units must be specified")
        if preferred_unit is None:
            self.preferred_unit = self.units[0]


def find_unit_spec(field: FieldInfo) -> UnitSpec | None:
    metadata = field.metadata
    for m in metadata:
        if isinstance(m, UnitSpec):
            return m
    return None


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

    pk: int = None
    _slims_table: SLIMSTABLES

    @field_validator("*", mode="before")
    def validate(cls, value, info: ValidationInfo):
        if isinstance(value, SlimsColumn):
            if value.datatype == "QUANTITY":
                unit_spec = find_unit_spec(cls.model_fields[info.field_name])
                if unit_spec is None:
                    msg = f'Quantity field "{info.field_name}" must be annotated with a UnitSpec'
                    raise TypeError(msg)
                if value.unit not in unit_spec.units:
                    msg = f'Unexpected unit "{value.unit}" for field {info.field_name}, Expected {unit_spec.units}'
                    raise ValueError(msg)
            return value.value
        else:
            return value

    @field_serializer("*")
    def serialize(self, field, info):
        unit_spec = find_unit_spec(self.model_fields[info.field_name])
        if unit_spec and field is not None:
            quantity = {
                "amount": field,
                "unit_display": unit_spec.preferred_unit,
            }
            # quantity["unit_pk"] = 6 if unit_spec.preferred_unit == "g" else 15
            return quantity
        elif isinstance(field, datetime):
            return int(field.timestamp() * 10**3)
        else:
            return field

    # TODO: Add links - need Record.json_entity['links']['self']
    # TODO: Add Table - need Record.json_entity['tableName']
    # TODO: Support attachments


class SlimsClient:
    def __init__(self, url=None, username=None, password=None):
        self.url = url or config.slims_url
        self.db: Slims = None

        self.connect(
            self.url,
            username or config.slims_username,
            password or config.slims_password.get_secret_value(),
        )

    def connect(self, url: str, username: str, password: str):
        self.db = Slims(
            "slims",
            url,
            username,
            password,
        )

    def fetch(
        self,
        table: SLIMSTABLES,
        *args,
        sort: Optional[str | list[str]] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ) -> list[SlimsRecord]:
        """Fetch from the SLIMS database

        Args:
            table (str): SLIMS table to query
            sort (str | list[str], optional): Fields to sort by; e.g. date
            start (int, optional):  The first row to return
            end (int, optional): The last row to return
            *args (Slims.criteria.Criterion): Optional criteria to apply
            **kwargs (dict[str,str]): "field=value" filters

        Returns:
            records (list[SlimsRecord] | None): Matching records, if any
        """
        criteria = conjunction()
        for arg in args:
            if isinstance(arg, Criterion):
                criteria.add(arg)

        for k, v in kwargs.items():
            criteria.add(equals(k, v))
        try:
            records = self.db.fetch(
                table,
                criteria,
                sort=sort,
                start=start,
                end=end,
            )
        except _SlimsApiException:
            raise
            return None  # TODO: Raise or return empty list?

        return records

    def fetch_unit(self, unit_name: str) -> SlimsRecord:
        return self.fetch("Unit", unit_name=unit_name)[0]

    @lru_cache(maxsize=None)
    def fetch_pk(self, table: SLIMSTABLES, *args, **kwargs) -> int | None:
        records = self.fetch(table, *args, **kwargs)
        if len(records) > 0:
            return records[0].pk()
        else:
            return None

    def fetch_user(self, user_name: str):
        return self.fetch("User", user_userName=user_name)

    def add(self, table: SLIMSTABLES, data: dict):
        record = self.db.add(table, data)
        logger.info(f"SLIMS Add: {table}/{record.pk()}")
        return record

    def update(self, table: SLIMSTABLES, pk: int, data: dict):
        record = self.db.fetch_by_pk(table, pk)
        if record is None:
            raise ValueError('No data in SLIMS "{table}" table for pk "{pk}"')
        new_record = record.update(data)
        logger.info(f"SLIMS Update: {table}/{pk}")
        return new_record

    def rest_link(self, table: SLIMSTABLES, **kwargs):
        base_url = f"{self.url}/rest/{table}"
        queries = [f"?{k}={v}" for k, v in kwargs.items()]
        return base_url + "".join(queries)

    def add_model(self, model: SlimsBaseModel, *args, **kwargs):
        fields_to_include = set(args) or None
        fields_to_exclude = set(kwargs.get("exclude", []))
        fields_to_exclude.add("pk")
        rtn = self.add(
            model._slims_table,
            model.model_dump(
                include=fields_to_include,
                exclude=fields_to_exclude,
                **kwargs,
                by_alias=True,
            ),
        )
        return type(model).model_validate(rtn)

    def update_model(self, model: SlimsBaseModel, *args, **kwargs):
        fields_to_include = set(args) or None
        rtn = self.update(
            model._slims_table,
            model.pk,
            model.model_dump(
                include=fields_to_include,
                by_alias=True,
                **kwargs,
            ),
        )
        return type(model).model_validate(rtn)
