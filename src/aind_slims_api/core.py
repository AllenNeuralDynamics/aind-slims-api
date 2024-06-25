"""Contents:

Utilities for creating pydantic models for SLIMS data:
    SlimsBaseModel - to be subclassed for SLIMS pydantic models
    UnitSpec - To be included in a type annotation of a Quantity field

SlimsClient - Basic wrapper around slims-python-api client with convenience
    methods and integration with SlimsBaseModel subtypes
"""

from datetime import datetime
from functools import lru_cache
from pydantic import (
    BaseModel,
    ValidationInfo,
    field_serializer,
    field_validator,
)
from pydantic.fields import FieldInfo
import logging
from typing import Literal, Optional

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
    """Used in type annotation metadata to specify units"""

    units: list[str]
    preferred_unit: str = None

    def __init__(self, *args, preferred_unit=None):
        """Set list of acceptable units from args, and preferred_unit"""
        self.units = args
        if len(self.units) == 0:
            raise ValueError("One or more units must be specified")
        if preferred_unit is None:
            self.preferred_unit = self.units[0]


def _find_unit_spec(field: FieldInfo) -> UnitSpec | None:
    """Given a Pydantic FieldInfo, find the UnitSpec in its metadata"""
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
    json_entity: dict = None
    _slims_table: SLIMSTABLES

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
    # TODO: Support attachments


class SlimsClient:
    """Wrapper around slims-python-api client with convenience methods"""

    def __init__(self, url=None, username=None, password=None):
        """Create object and try to connect to database"""
        self.url = url or config.slims_url
        self.db: Optional[Slims] = None

        self.connect(
            self.url,
            username or config.slims_username,
            password or config.slims_password.get_secret_value(),
        )

    def connect(self, url: str, username: str, password: str):
        """Connect to the database"""
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
        except _SlimsApiException as e:
            # TODO: Add better error handling
            #  Let's just raise error for the time being
            raise e

        return records

    @lru_cache(maxsize=None)
    def fetch_pk(self, table: SLIMSTABLES, *args, **kwargs) -> int | None:
        """SlimsClient.fetch but returns the pk of the first returned record"""
        records = self.fetch(table, *args, **kwargs)
        if len(records) > 0:
            return records[0].pk()
        else:
            return None

    def fetch_user(self, user_name: str):
        """Fetches a user by username"""
        return self.fetch("User", user_userName=user_name)

    def add(self, table: SLIMSTABLES, data: dict):
        """Add a SLIMS record to a given SLIMS table"""
        record = self.db.add(table, data)
        logger.info(f"SLIMS Add: {table}/{record.pk()}")
        return record

    def update(self, table: SLIMSTABLES, pk: int, data: dict):
        """Update a SLIMS record"""
        record = self.db.fetch_by_pk(table, pk)
        if record is None:
            raise ValueError(f'No data in SLIMS "{table}" table for pk "{pk}"')
        new_record = record.update(data)
        logger.info(f"SLIMS Update: {table}/{pk}")
        return new_record

    def rest_link(self, table: SLIMSTABLES, **kwargs):
        """Construct a url link to a SLIMS table with arbitrary filters"""
        base_url = f"{self.url}/rest/{table}"
        queries = [f"?{k}={v}" for k, v in kwargs.items()]
        return base_url + "".join(queries)

    def add_model(self, model: SlimsBaseModel, *args, **kwargs) -> SlimsBaseModel:
        """Given a SlimsBaseModel object, add it to SLIMS
        Args
            model (SlimsBaseModel): object to add
            *args (str): fields to include in the serialization
            **kwargs: passed to model.model_dump()

        Returns
            An instance of the same type of model, with data from
            the resulting SLIMS record
        """
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
        """Given a SlimsBaseModel object, update its (existing) SLIMS record

        Args
            model (SlimsBaseModel): object to update
            *args (str): fields to include in the serialization
            **kwargs: passed to model.model_dump()

        Returns
            An instance of the same type of model, with data from
            the resulting SLIMS record
        """
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
