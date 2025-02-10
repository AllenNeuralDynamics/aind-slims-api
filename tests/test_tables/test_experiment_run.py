"""Tests methods in experiment_run module"""

import unittest

from aind_slims_api.tables.experiment_run import ExperimentRun


class TestExperimentRun(unittest.TestCase):
    """Test init method for ExperimentRun class."""

    def test_init(self):
        """Tests init method"""
        model = ExperimentRun(xprn_pk=0)
        self.assertEqual(0, model.xprn_pk)


if __name__ == "__main__":
    unittest.main()
