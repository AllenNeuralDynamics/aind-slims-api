"""Tests functions in filters"""

import unittest

from slims.criteria import (
    between_inclusive,
    disjunction,
    is_na,
    is_not,
    is_not_one_of,
    is_one_of,
)

from aind_slims_api import filters
from aind_slims_api.models.unit import SlimsUnit
from aind_slims_api.models.user import SlimsUser


class TestFilters(unittest.TestCase):
    """Tests filter validation and utility functions."""

    def test_resolve_model_alias_invalid(self):
        """Tests resolve_model_alias method raises expected error with an
        invalid alias name.
        """
        with self.assertRaises(ValueError):
            filters.resolve_model_alias(SlimsUnit, "not_an_alias")

    def test__validate_field_name_failure(self):
        """Tests _validate_field_name method raises expected error with an
        invalid field name.
        """
        with self.assertRaises(ValueError):
            filters._validate_field_name(SlimsUnit, "not_an_alias")

    def test_validate_criteria_is_one_of(self):
        """Tests _validate_criteria method with an is_one_of criterion."""
        filters.validate_criteria(
            SlimsUser,
            is_one_of("username", ["LKim", "JSmith"]),
        )

    def test_validate_criteria_is_not_one_of(self):
        """Tests _validate_criteria method with an is_not_one_of
        criterion.
        """
        filters.validate_criteria(
            SlimsUser,
            is_not_one_of("username", ["LKim", "JSmith"]),
        )

    def test_validate_criteria_between_inclusive(self):
        """Tests _validate_criteria method with an between_inclusive criterion."""
        filters.validate_criteria(
            SlimsUser,
            between_inclusive("username", "LKim", "JSmith"),
        )

    def test_validate_criteria_is_na(self):
        """Tests _validate_criteria method with an is_na criterion."""
        filters.validate_criteria(
            SlimsUser,
            is_na("username"),
        )

    def test_resolve_criteria_is_na(self):
        """Tests _resolve_criteria method with an is_na criterion."""
        filters.resolve_criteria(
            SlimsUser,
            is_na("username"),
        )

    def test_validate_criteria_is_not(self):
        """Tests _validate_criteria method with an is_not criterion."""
        filters.validate_criteria(
            SlimsUser,
            is_not(is_one_of("username", ["LKim", "JSmith"])),
        )

    def test_validate_criteria_disjunction(self):
        """Tests _validate_criteria method with an is_not criterion."""
        criteria = (
            disjunction()
            .add(is_one_of("username", ["LKim"]))
            .add(is_one_of("username", ["JSmith"]))
        )
        filters.validate_criteria(
            SlimsUser,
            criteria,
        )


if __name__ == "__main__":
    unittest.main()
