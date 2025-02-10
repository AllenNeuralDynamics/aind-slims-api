"""Tests methods in experiment module"""

import unittest

from aind_slims_api.tables.experiment import Experiment


class TestExperiment(unittest.TestCase):
    """Test init method for Experiment class."""

    def test_init(self):
        """Tests init method"""
        model = Experiment(xprm_pk=0)
        self.assertEqual(0, model.xprm_pk)


if __name__ == "__main__":
    unittest.main()
