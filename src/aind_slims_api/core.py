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
from typing import Any, Optional, Type, TypeVar, get_type_hints

from pydantic import ValidationError
from requests import Response
from slims.criteria import Criterion, Expression, Junction, conjunction, equals
from slims.internal import Record as SlimsRecord
from slims.slims import Slims, _SlimsApiException

from aind_slims_api import config
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models import SlimsAttachment
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

        if isinstance(sort, str):
            sort = [sort]

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
        """Given a SlimsBaseModel object, resolve its pk to the actual value

        Notes
        -----
        - Raises ValueError if the alias cannot be resolved
        - Resolves the validation alias for a given field name
        - If prefixed with `-` will return the validation alias prefixed with
         `-`
        """
        has_prefix = attr_name.startswith("-")
        _attr_name = attr_name.lstrip("-")
        for field_name, field_info in model.model_fields.items():
            if (
                field_name == _attr_name
                and field_info.validation_alias
                and isinstance(field_info.validation_alias, str)
            ):
                alias = field_info.validation_alias
                if has_prefix:
                    return f"-{alias}"
                return alias
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

    @staticmethod
    def _resolve_criteria(
        model_type: Type[SlimsBaseModelTypeVar], criteria: Criterion
    ) -> Criterion:
        """Resolves criterion field name to serialization alias in a criterion."""
        if isinstance(criteria, Junction):
            criteria.members = [
                SlimsClient._resolve_criteria(model_type, sub_criteria)
                for sub_criteria in criteria.members
            ]
            return criteria
        elif isinstance(criteria, Expression):
            criteria.criterion["fieldName"] = SlimsClient.resolve_model_alias(
                model_type,
                criteria.criterion["fieldName"],
            )
            return criteria
        else:
            raise ValueError(f"Invalid criterion type: {type(criteria)}")

    @staticmethod
    def _validate_field_name(
        model_type: Type[SlimsBaseModelTypeVar],
        field_name: str,
    ) -> None:
        """Check if field_name is a field on a model. Raises a ValueError if it
        is not.
        """
        field_type_map = get_type_hints(model_type)
        if field_name not in field_type_map:
            raise ValueError(f"{field_name} is not a field on {model_type}.")

    @staticmethod
    def _validate_field_value(
        model_type: Type[SlimsBaseModelTypeVar],
        field_name: str,
        field_value: Any,
    ) -> None:
        """Check if field_value is a compatible with
        the type associated with that field. Raises a ValueError if it is not.
        """
        field_type_map = get_type_hints(model_type)
        field_type = field_type_map[field_name]
        if not isinstance(field_value, field_type):
            raise ValueError(
                f"{field_value} is incompatible with {field_type}"
                f" for field {field_name}"
            )

    @staticmethod
    def _validate_criteria(
        model_type: Type[SlimsBaseModelTypeVar], criteria: Criterion
    ) -> None:
        """Validates that the types used in a criterion are compatible with the
        types on the model. Raises a ValueError if they are not.
        """
        if isinstance(criteria, Junction):
            for sub_criteria in criteria.members:
                SlimsClient._validate_criteria(model_type, sub_criteria)
        elif isinstance(criteria, Expression):
            SlimsClient._validate_field_name(
                model_type,
                criteria.criterion["fieldName"],
            )
            SlimsClient._validate_field_value(
                model_type,
                criteria.criterion["fieldName"],
                criteria.criterion["value"],
            )
        else:
            raise ValueError(f"Invalid criterion type: {type(criteria)}")

    @staticmethod
    def _resolve_filter_args(
        model: Type[SlimsBaseModelTypeVar],
        *args: Criterion,
        sort: list[str] = [],
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ) -> tuple[list[Criterion], list[str], Optional[int], Optional[int]]:
        """Validates filter arguments and resolves field names to SLIMS API
        column names.
        """
        criteria = deepcopy(list(args))
        criteria.extend(map(lambda item: equals(item[0], item[1]), kwargs.items()))
        resolved_criteria: list[Criterion] = []
        for criterion in criteria:
            SlimsClient._validate_criteria(model, criterion)
            resolved_criteria.append(SlimsClient._resolve_criteria(model, criterion))
        resolved_sort = [
            SlimsClient.resolve_model_alias(model, sort_key) for sort_key in sort
        ]
        if start is not None and end is None or end is not None and start is None:
            raise ValueError("Must provide both start and end or neither for fetch.")
        return resolved_criteria, resolved_sort, start, end

    def fetch_models(
        self,
        model: Type[SlimsBaseModelTypeVar],
        *args: Criterion,
        sort: str | list[str] = [],
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ) -> list[SlimsBaseModelTypeVar]:
        """Fetch records from SLIMS and return them as SlimsBaseModel objects.

        Returns
        -------
        tuple:
            list:
                Validated SlimsBaseModel objects

        Notes
        -----
        - kwargs are mapped to field alias names and used as equality filters
         for the fetch.
        """
        if isinstance(sort, str):
            sort = [sort]

        criteria, resolved_sort, start, end = self._resolve_filter_args(
            model,
            *args,
            sort=sort,
            start=start,
            end=end,
            **kwargs,
        )
        response = self.fetch(
            model._slims_table,
            *criteria,
            sort=resolved_sort,
            start=start,
            end=end,
        )
        return self._validate_models(model, response)

    def fetch_model(
        self,
        model: Type[SlimsBaseModelTypeVar],
        *args: Criterion,
        **kwargs,
    ) -> SlimsBaseModelTypeVar | None:
        """Fetch a single record from SLIMS and return it as a validated
         SlimsBaseModel object.

        Notes
        -----
        - kwargs are mapped to field alias values
        - sorts records on created_on in descending order and returns the first
        """
        records = self.fetch_models(
            model,
            *args,
            sort="-created_on",
            start=0,  # slims rows appear to be 0-indexed
            end=1,
            **kwargs,
        )
        if len(records) > 0:
            logger.debug(f"Found {len(records)} records for {model}.")
        if len(records) < 1:
            raise SlimsRecordNotFound("No record found.")
        return records[0]

    @staticmethod
    def _create_get_entities_body(
        *args: Criterion,
        sort: list[str] = [],
        start: Optional[int] = None,
        end: Optional[int] = None,
    ) -> dict[str, Any]:
        """Creates get entities body for SLIMS API request."""
        body: dict[str, Any] = {
            "sortBy": sort,
            "startRow": start,
            "endRow": end,
        }
        if args:
            criteria = conjunction()
            for arg in args:
                criteria.add(arg)
            body["criteria"] = criteria.to_dict()

        return body

    def fetch_attachments(
        self,
        record: SlimsBaseModel,
        *args,
        sort: str | list[str] = [],
        start: Optional[int] = None,
        end: Optional[int] = None,
        **kwargs,
    ) -> list[SlimsAttachment]:
        """Fetch attachments for a given record.

        Notes
        -----
        - kwargs are mapped to field alias values
        """
        if isinstance(sort, str):
            sort = [sort]

        criteria, sort, start, end = self._resolve_filter_args(
            SlimsAttachment,
            *args,
            sort=sort,
            start=start,
            end=end,
            **kwargs,
        )
        return self._validate_models(
            SlimsAttachment,
            self.db.slims_api.get_entities(
                f"attachment/{record._slims_table}/{record.pk}",
                body=self._create_get_entities_body(
                    *criteria,
                    sort=sort,
                    start=start,
                    end=end,
                ),
            ),
        )

    def fetch_attachment(
        self,
        record: SlimsBaseModel,
        *args,
        **kwargs,
    ) -> SlimsAttachment:
        """Fetch attachments for a given record.

        Notes
        -----
        - kwargs are mapped to field alias values
        - sorts records on created_on in descending order and returns the first
        """
        records = self.fetch_attachments(
            record,
            *args,
            sort="-created_on",
            start=0,  # slims rows appear to be 0-indexed
            end=1,
            **kwargs,
        )
        if len(records) > 0:
            logger.debug(f"Found {len(records)} records for {record}.")
        if len(records) < 1:
            raise SlimsRecordNotFound("No record found.")
        return records[0]

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
