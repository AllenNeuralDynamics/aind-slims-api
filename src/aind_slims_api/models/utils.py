"""Utility functions and classes for working with slims models.
"""

from typing import Optional

from pydantic.fields import FieldInfo


class UnitSpec:
    """Used in type annotation metadata to specify units"""

    units: tuple[str]
    preferred_unit: Optional[str] = None

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
