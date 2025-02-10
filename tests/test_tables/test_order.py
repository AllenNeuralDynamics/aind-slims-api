"""Tests methods in order module"""

import unittest

from aind_slims_api.tables.order import Order


class TestOrder(unittest.TestCase):
    """Test init method for Order class."""

    def test_init(self):
        """Tests init method"""
        model = Order(ordr_pk=0)
        self.assertEqual(0, model.ordr_pk)


if __name__ == "__main__":
    unittest.main()
