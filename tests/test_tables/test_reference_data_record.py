"""Tests methods in reference_data_record module"""

import unittest

from aind_slims_api.tables.reference_data_record import ReferenceDataRecord


class TestReferenceDataRecord(unittest.TestCase):
    """Test init method for ReferenceDataRecord class."""

    def test_init(self):
        """Tests init method"""
        model = ReferenceDataRecord(rdrc_pk=0)
        self.assertEqual(0, model.rdrc_pk)


if __name__ == "__main__":
    unittest.main()
