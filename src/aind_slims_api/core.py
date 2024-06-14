"""Contents:

Utilities for creating pydantic models for SLIMS data:
    SlimsBaseModel - to be subclassed for SLIMS pydantic models
    UnitSpec - To be included in a type annotation of a Quantity field

SlimsClient - Basic wrapper around slims-python-api client with convenience
    methods and integration with SlimsBaseModel subtypes
"""

import logging
from functools import lru_cache
from typing import Literal, Optional

from slims.criteria import Criterion, conjunction, equals
from slims.internal import Record as SlimsRecord
from slims.slims import Slims, _SlimsApiException

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
