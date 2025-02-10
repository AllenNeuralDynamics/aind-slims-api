"""Tests methods in result module"""

import unittest

from aind_slims_api.tables.result import Result


class TestResult(unittest.TestCase):
    """Test init method for Result class."""

    def test_init(self):
        """Tests init method"""
        model = Result(rslt_pk=0)
        self.assertEqual(0, model.rslt_pk)


if __name__ == "__main__":
    unittest.main()
