"""Tests methods in content module"""

import unittest

from aind_slims_api.tables.content import Content


class TestContent(unittest.TestCase):
    """Test init method for Content class."""

    def test_init(self):
        """Tests init method"""
        model = Content(cntn_pk=0)
        self.assertEqual(0, model.cntn_pk)


if __name__ == "__main__":
    unittest.main()
