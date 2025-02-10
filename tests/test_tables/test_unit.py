"""Tests methods in unit module"""

import unittest

from aind_slims_api.tables.unit import Unit


class TestUnit(unittest.TestCase):
    """Test init method for Unit class."""

    def test_init(self):
        """Tests init method"""
        model = Unit(unit_pk=0)
        self.assertEqual(0, model.unit_pk)


if __name__ == "__main__":
    unittest.main()
