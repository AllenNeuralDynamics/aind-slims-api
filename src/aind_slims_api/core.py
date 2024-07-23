"""Contents:

Utilities for creating pydantic models for SLIMS data:
    SlimsBaseModel - to be subclassed for SLIMS pydantic models
    UnitSpec - To be included in a type annotation of a Quantity field

SlimsClient - Basic wrapper around slims-python-api client with convenience
    methods and integration with SlimsBaseModel subtypes
"""

import base64
import logging
from copy import deepcopy
from functools import lru_cache
from typing import Optional, Type, TypeVar

from pydantic import ValidationError
from requests import Response
from slims.criteria import Criterion, conjunction, equals
from slims.internal import Record as SlimsRecord
from slims.slims import Slims, _SlimsApiException

from aind_slims_api import config
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.attachment import SlimsAttachment
from aind_slims_api.models.base import SlimsBaseModel
from aind_slims_api.types import SLIMS_TABLES

logger = logging.getLogger(__name__)


SlimsBaseModelTypeVar = TypeVar("SlimsBaseModelTypeVar", bound=SlimsBaseModel)


class SlimsClient:
    """Wrapper around slims-python-api client with convenience methods"""

    db: Slims

    def __init__(self, url=None, username=None, password=None):
        """Create object and try to connect to database"""
        self.url = url or config.slims_url

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
        table: SLIMS_TABLES,
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

    @staticmethod
    def resolve_model_alias(
        model: Type[SlimsBaseModelTypeVar],
        attr_name: str,
    ) -> str:
        """Given a SlimsBaseModel object, resolve its pk to the actual value"""
        for field_name, field_info in model.model_fields.items():
            if field_name == attr_name and field_info.alias:
                return field_info.alias
        else:
            raise ValueError(f"Cannot resolve alias for {attr_name} on {model}")

    @staticmethod
    def _validate_models(
        model_type: Type[SlimsBaseModelTypeVar], records: list[SlimsRecord]
    ) -> list[SlimsBaseModelTypeVar]:
        """Validate a list of SlimsBaseModel objects. Logs errors for records
        that fail pydantic validation."""
        validated = []
        for record in records:
            try:
                validated.append(model_type.model_validate(record))
            except ValidationError as e:
                logger.error(f"SLIMS data validation failed, {repr(e)}")
        return validated

    def fetch_models(
        self,
        model: Type[SlimsBaseModelTypeVar],
        *args,
        sort: Optional[str | list[str]] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ) -> list[SlimsBaseModelTypeVar]:
        """Fetch records from SLIMS and return them as SlimsBaseModel objects

        Returns
        -------
        tuple:
            list:
                Validated SlimsBaseModel objects

        Notes
        -----
        - kwargs are mapped to field alias values
        """
        resolved_kwargs = deepcopy(model._base_fetch_filters)
        for name, value in kwargs.items():
            resolved_kwargs[self.resolve_model_alias(model, name)] = value
        logger.debug("Resolved kwargs: %s", resolved_kwargs)
        resolved_sort: Optional[str | list[str]] = None
        if sort is not None:
            if isinstance(sort, str):
                resolved_sort = self.resolve_model_alias(model, sort)
            else:
                resolved_sort = [
                    self.resolve_model_alias(model, sort_key) for sort_key in sort
                ]
        logger.debug("Resolved sort: %s", resolved_sort)
        response = self.fetch(
            model._slims_table,  # TODO: consider changing fetch method
            *args,
            sort=resolved_sort,
            start=start,
            end=end,
            **resolved_kwargs,
        )
        return self._validate_models(model, response)

    def fetch_model(
        self,
        model: Type[SlimsBaseModelTypeVar],
        *args,
        sort: Optional[str | list[str]] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ) -> SlimsBaseModelTypeVar | None:
        """Fetch a single record from SLIMS and return it as a validated
         SlimsBaseModel object.

        Notes
        -----
        - kwargs are mapped to field alias values
        """
        records = self.fetch_models(
            model,
            *args,
            sort=sort,
            start=start,
            end=end,
            **kwargs,
        )
        if len(records) > 0:
            logger.debug(f"Found {len(records)} records for {model}.")
        if len(records) < 1:
            raise SlimsRecordNotFound("No record found.")
        return records[0]

    def fetch_attachments(
        self,
        record: SlimsBaseModel,
    ) -> list[SlimsAttachment]:
        """Fetch attachments for a given record."""
        return self._validate_models(
            SlimsAttachment,
            self.db.slims_api.get_entities(
                f"attachment/{record._slims_table}/{record.pk}"
            ),
        )

    def fetch_attachment_content(
        self,
        attachment: int | SlimsAttachment,
    ) -> Response:
        """Fetch attachment content for a given attachment.

        Parameters
        -----------
        attachment: int | SlimsAttachment
            The primary key of the attachment or an attachment object
        """
        if isinstance(attachment, SlimsAttachment):
            attachment = attachment.pk

        return self.db.slims_api.get(f"repo/{attachment}")

    @lru_cache(maxsize=None)
    def fetch_pk(self, table: SLIMS_TABLES, *args, **kwargs) -> int | None:
        """SlimsClient.fetch but returns the pk of the first returned record"""
        records = self.fetch(table, *args, **kwargs)
        if len(records) > 0:
            return records[0].pk()
        else:
            return None

    def fetch_user(self, user_name: str):
        """Fetches a user by username"""
        return self.fetch("User", user_userName=user_name)

    def add(self, table: SLIMS_TABLES, data: dict):
        """Add a SLIMS record to a given SLIMS table"""
        record = self.db.add(table, data)
        logger.info(f"SLIMS Add: {table}/{record.pk()}")
        return record

    def update(self, table: SLIMS_TABLES, pk: int, data: dict):
        """Update a SLIMS record"""
        record = self.db.fetch_by_pk(table, pk)
        if record is None:
            raise ValueError(f'No data in SLIMS "{table}" table for pk "{pk}"')
        new_record = record.update(data)
        logger.info(f"SLIMS Update: {table}/{pk}")
        return new_record

    def rest_link(self, table: SLIMS_TABLES, **kwargs):
        """Construct a url link to a SLIMS table with arbitrary filters"""
        base_url = f"{self.url}/rest/{table}"
        queries = [f"?{k}={v}" for k, v in kwargs.items()]
        return base_url + "".join(queries)

    def add_model(
        self, model: SlimsBaseModelTypeVar, *args, **kwargs
    ) -> SlimsBaseModelTypeVar:
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
        fields_to_exclude.update(["pk", "attachments", "slims_api"])
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
        if model.pk is None:
            raise ValueError("Cannot update model without a pk")

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

    def add_attachment_content(
        self,
        record: SlimsBaseModel,
        name: str,
        content: bytes | str,
    ) -> int:
        """Add an attachment to a SLIMS record

        Returns
        -------
        int: Primary key of the attachment added.

        Notes
        -----
        - Returned attachment does not contain the name of the attachment in
         Slims, this requires a separate fetch.
        """
        if record.pk is None:
            raise ValueError("Cannot add attachment to a record without a pk")

        if isinstance(content, str):
            content = content.encode("utf-8")

        response = self.db.slims_api.post(
            url="repo",
            body={
                "attm_name": name,
                "atln_recordPk": record.pk,
                "atln_recordTable": record._slims_table,
                "contents": base64.b64encode(content).decode("utf-8"),
            },
        )
        response.raise_for_status()
        return int(response.text)
