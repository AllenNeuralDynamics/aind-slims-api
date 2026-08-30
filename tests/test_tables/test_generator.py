"""Tests methods in the generator module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

# noinspection PyProtectedMember
from aind_slims_api.tables.generator import _map_column, generate_module

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "resources"


class TestMethods(unittest.TestCase):
    """Tests methods in module."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class by preloading json files"""

        with open(RESOURCES_DIR / "example_fetch_mouse_response.json") as f:
            mouse_contents = json.load(f)
        with open(RESOURCES_DIR / "example_fetch_reagent_content.json") as f:
            reagent_contents = json.load(f)
        # noinspection PyTypeChecker
        first_record = Record(json_entity=mouse_contents[0], slims_api=None)
        # noinspection PyTypeChecker
        second_record = Record(reagent_contents[0]["json_entity"], slims_api=None)
        cls.example_records = [first_record, second_record]

    def test_map_column(self):
        """Tests a few edge cases for the _map_column method."""

        c1 = {
            "datatype": "FOREIGN_KEY",
            "name": "cntn_fk_product_strain",
            "title": "Product (filtering without version)",
            "position": 39,
            "value": None,
            "hidden": False,
            "editable": True,
            "foreignTable": "Product",
            "displayValue": None,
            "displayField": "prdc_name",
            "foreignDisplayColumn": None,  # Missing field should return None
        }
        c2 = {
            "datatype": "MULTIPLE_FOREIGN_KEY",
            "name": "cntn_fk_product_strains",
            "title": "Product (filtering without version)",
            "position": 40,
            "value": None,
            "hidden": False,
            "editable": True,
            "foreignTable": None,  # Missing field should return None
            "displayValue": None,
            "displayField": "prdc_name",
            "foreignDisplayColumn": "prdc_name",
        }
        c3 = {
            "datatype": "MULTIPLE_ENUM",
            "name": "rslt_cf_cameraNames2",
            "title": "Camera Names",
            "position": 19,
            "value": ["Face camera"],
            "hidden": False,
            "editable": True,
            "joinedValue": "Face camera",
        }
        c4 = {
            "datatype": "UNKNOWN_DATATYPE",
            "name": "rslt_cf_cameraNames2",
            "title": "Camera Names",
            "position": 19,
            "value": ["Face camera"],
            "hidden": False,
            "editable": True,
            "joinedValue": "Face camera",
        }

        mapped_c1 = _map_column(c1)
        mapped_c2 = _map_column(c2)
        mapped_c3 = _map_column(c3)
        mapped_c4 = _map_column(c4)

        expected_mapped_c3 = (
            "    rslt_cf_cameraNames2: Optional[List[str]] = "
            'Field(default=None, title="Camera Names")'
        )

        self.assertIsNone(mapped_c1)
        self.assertIsNone(mapped_c2)
        self.assertEqual(expected_mapped_c3, mapped_c3)
        self.assertIsNone(mapped_c4)

    @patch("builtins.open")
    def test_generator_default_path(self, mock_open: MagicMock):
        """Tests generator method when write_path is None."""
        records = self.example_records
        generate_module(records=records, write_path=None)
        # Assert default output path is correct
        mock_open.assert_any_call(Path("content.py"), "w")

    @patch("builtins.open")
    def test_generator_defined_path(self, mock_open: MagicMock):
        """Tests generator method when write_path is not None."""
        records = self.example_records
        generate_module(records=records, write_path=Path("abc.py"))
        # Assert default output path is correct
        mock_open.assert_any_call(Path("abc.py"), "w")


if __name__ == "__main__":
    unittest.main()
