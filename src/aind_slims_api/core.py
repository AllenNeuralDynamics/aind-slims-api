from datetime import timezone as tz
import datetime
from enum import Enum
import os
import json
from dataclasses import dataclass
from pydantic import BaseModel, BeforeValidator, ValidationError
import requests
from requests.auth import HTTPBasicAuth
import logging
from typing import Annotated, Any, Self, Union, Literal, Optional
import math

from slims.slims import Slims, _SlimsApiException
from slims.internal import Column as SlimsColumn, Record as SlimsRecord
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


class PydanticFromSlims(BaseModel):
    """Pydantic BaseModel with .from_slims_record factory method"""

    @classmethod
    def from_slims_record(cls, record: SlimsRecord) -> Self:
        fields_dict = {}
        for field in cls.model_fields.keys():
            if hasattr(record, field):
                fields_dict[field] = record.__getattribute__(field).value
        try:
            obj = cls(**fields_dict)
        except ValidationError as e:
            obj = fields_dict
            raise  # TODO: return dict or raise error?
        return obj

    # TODO: Add serialization method? could be hard to abstract usefully


class SlimsClient:
    def __init__(self, url=None, username=None, password=None):
        self.db: Slims = None

        self.connect(
            url or config.slims_url,
            username or config.slims_username,
            password or config.slims_password,
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
    ) -> list[SlimsRecord] | None:
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
            return None  # TODO: Raise or return empty list?

        return records

    def format_quantity(self, quantity: Union[float, None], unit: str) -> dict | None:
        if quantity is None or math.isnan(quantity):
            return None
        else:
            return {
                "amount": quantity,
                "unit_pk": self.fetch_unit(unit).pk(),
                "unit_display": unit,
            }

    def convert_quantity(self, value: float, from_unit: str, to_unit: str):
        # TODO:
        from_unit_pk = self.fetch_unit(from_unit)
        to_unit_pk = self.fetch_unit(to_unit)

    def fetch_unit(self, unit_name: str) -> SlimsRecord:
        return self.fetch("Unit", unit_name=unit_name)[0]

    def fetch_pk(self, *args, **kwargs) -> int | None:
        records = self.fetch(*args, **kwargs, pydantic_model=None)
        if len(records) > 0:
            return records[0].pk()
        else:
            return None

    def fetch_user(self, user_name: str):
        return self.fetch("User", user_userName=user_name)

    def add(self, table: SLIMSTABLES, data: dict):
        self.db.add(table, data)
        logger.info(f"SLIMS Post: {table}")

    def update(self, table: SLIMSTABLES, pk: int, data: dict):
        record = self.db.fetch_by_pk(table, pk)
        if record is None:
            raise ValueError
        record.update(data)
