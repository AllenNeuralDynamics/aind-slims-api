"""Utility functions for filtering and sorting data in the SLIMS API.
"""

import logging
from copy import deepcopy
from typing import Any, Optional, Type, TypeVar, get_type_hints

from slims.criteria import Criterion, Expression, Junction, equals
from aind_slims_api.models.base import SlimsBaseModel

logger = logging.getLogger(__name__)

SlimsBaseModelTypeVar = TypeVar("SlimsBaseModelTypeVar", bound=SlimsBaseModel)


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


def _resolve_criteria(
    model_type: Type[SlimsBaseModelTypeVar],
    criteria: Criterion,
) -> Criterion:
    """Resolves criterion field name to serialization alias in a criterion."""

    if isinstance(criteria, Junction):
        criteria.members = [
            _resolve_criteria(model_type, sub_criteria)
            for sub_criteria in criteria.members
        ]
        return criteria
    elif isinstance(criteria, Expression):
        if criteria.criterion["fieldName"] == "isNaFilter":
            criteria.criterion["value"] = resolve_model_alias(
                model_type,
                criteria.criterion["value"],
            )
        else:
            criteria.criterion["fieldName"] = resolve_model_alias(
                model_type,
                criteria.criterion["fieldName"],
            )
        return criteria
    else:
        raise ValueError(f"Invalid criterion type: {type(criteria)}")


def validate_criterion(
    model_type: Type[SlimsBaseModelTypeVar],
    field_name: str,
) -> None:
    """Check if field_name is a field on a model. Raises a ValueError if it
    is not.
    """
    field_type_map = get_type_hints(model_type)
    if field_name not in field_type_map:
        raise ValueError(f"{field_name} is not a field on {model_type}.")



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


def _validate_criteria(
    model_type: Type[SlimsBaseModelTypeVar], criteria: Criterion
) -> None:
    """Validates that the types used in a criterion are compatible with the
    types on the model. Raises a ValueError if they are not.

    Notes
    -----
    - TODO: Consider using pydantic's validation error or some other more
     appropriate exception?
    """
    if isinstance(criteria, Junction):
        for sub_criteria in criteria.members:
            _validate_criteria(model_type, sub_criteria)
    elif isinstance(criteria, Expression):
        if criteria.criterion["fieldName"] == "isNaFilter":
            _validate_field_name(
                model_type,
                criteria.criterion["value"],
            )
        elif criteria.criterion["operator"] in ["inSet", "notInSet"]:
            _validate_field_name(
                model_type,
                criteria.criterion["fieldName"],
            )
            for value in criteria.criterion["value"]:
                _validate_field_value(
                    model_type,
                    criteria.criterion["fieldName"],
                    value,
                )
        elif criteria.criterion["operator"] == "betweenInclusive":
            _validate_field_name(
                model_type,
                criteria.criterion["fieldName"],
            )
            _validate_field_value(
                model_type,
                criteria.criterion["fieldName"],
                criteria.criterion["start"],
            )
            _validate_field_value(
                model_type,
                criteria.criterion["fieldName"],
                criteria.criterion["end"],
            )
        else:
            _validate_field_name(
                model_type,
                criteria.criterion["fieldName"],
            )
            _validate_field_value(
                model_type,
                criteria.criterion["fieldName"],
                criteria.criterion["value"],
            )
    else:
        raise ValueError(f"Invalid criterion type: {type(criteria)}")


def resolve_filter_args(
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
        _validate_criteria(model, criterion)
        resolved_criteria.append(_resolve_criteria(model, criterion))
    resolved_sort = [
        resolve_model_alias(model, sort_key) for sort_key in sort
    ]
    if start is not None and end is None or end is not None and start is None:
        raise ValueError(
            "Must provide both start and end or neither for fetch.")
    return resolved_criteria, resolved_sort, start, end
