"""Tests methods in experiment_run_step_content module"""

import unittest

from aind_slims_api.tables.experiment_run_step_content import ExperimentRunStepContent


class TestExperimentRunStepContent(unittest.TestCase):
    """Test init method for ExperimentRunStepContent class."""

    def test_init(self):
        model = ExperimentRunStepContent(xrsc_pk=0)
        self.assertEqual(0, model.xrsc_pk)


if __name__ == "__main__":
    unittest.main()
