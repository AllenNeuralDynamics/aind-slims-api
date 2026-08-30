"""Tests methods in workflow module"""

import unittest

from aind_slims_api.tables.workflow import Workflow


class TestWorkflow(unittest.TestCase):
    """Test init method for Workflow class."""

    def test_init(self):
        """Tests init method"""
        model = Workflow(wrfl_pk=0)
        self.assertEqual(0, model.wrfl_pk)


if __name__ == "__main__":
    unittest.main()
