"""Tests methods in core package"""

import unittest
import os
from datetime import datetime
from pathlib import Path
from slims.internal import Record

from aind_slims_api.tables.core import get_value_or_none, records_to_models, \
    Quantity
from aind_slims_api.tables.content import Content
import json

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"


class TestMethods(unittest.TestCase):
    """Tests methods in module."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class by pre-loading json files"""

        with open(RESOURCES_DIR / "example_fetch_mouse_response.json") as f:
            mouse_contents = json.load(f)
        with open(RESOURCES_DIR / "example_fetch_reagent_content.json") as f:
            reagent_contents = json.load(f)
        first_record = Record(json_entity=mouse_contents[0], slims_api=None)
        second_record = Record(reagent_contents[0]["json_entity"], slims_api=None)
        cls.example_records = [first_record, second_record]

    def test_get_value_or_none_success(self):
        """Tests get_value_or_none when expected field is found."""

        val = get_value_or_none(self.example_records[0], "cntn_pk")
        self.assertEqual(3038, val)

    def test_get_value_or_none_failure(self):
        """Tests get_value_or_none when expected field is not found."""

        val = get_value_or_none(self.example_records[0], "no_such_field")
        self.assertIsNone(val)

    def test_records_to_models(self):
        """Tests records_to_models method."""

        models = records_to_models(records=self.example_records, model=Content)
        # Check a few of the fields
        self.assertEqual('123456', models[0].cntn_barCode)
        self.assertEqual(Quantity(value=25.2, unit='g'), models[0].cntn_cf_baselineWeight)
        self.assertEqual('PersonB', models[0].cntn_cf_contactPerson)
        self.assertEqual(datetime(2024, 5, 15, 5, 0), models[0].cntn_cf_dateOfBirth)
        self.assertEqual('rgntE00000027', models[1].cntn_barCode)

    # def test_records_to_models_na(self):
    #     """Tests records_to_models method when an NA type is encountered."""
    #
    #     models = records_to_models(records=self.example_records, model=Content)
    #     # Check a few of the fields
    #     second_model = models[1]
    #     self.assertEqual('123456', first_model.cntn_barCode)
    #     self.assertEqual(Quantity(value=25.2, unit='g'), first_model.cntn_cf_baselineWeight)
    #     self.assertEqual('PersonB', first_model.cntn_cf_contactPerson)
    #     self.assertEqual(datetime(2024, 5, 15, 5, 0), first_model.cntn_cf_dateOfBirth)


if __name__ == "__main__":
    unittest.main()
