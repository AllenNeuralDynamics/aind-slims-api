"""Tests methods in experiment_run_step module"""

import unittest

from aind_slims_api.tables.experiment_run_step import ExperimentRunStep


class TestExperimentRunStep(unittest.TestCase):
    """Test init method for ExperimentRunStep class."""

    def test_init(self):
        model = ExperimentRunStep(xprs_pk=0)
        self.assertEqual(0, model.xprs_pk)


if __name__ == "__main__":
    unittest.main()
