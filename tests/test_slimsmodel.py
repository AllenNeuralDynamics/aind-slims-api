""" Tests the generic SlimsBaseModel"""

import unittest
from datetime import datetime
from typing import Annotated, Optional

from pydantic import Field
from slims.internal import Column, Record

from aind_slims_api.core import SlimsBaseModel
from aind_slims_api.models.utils import UnitSpec


class TestSlimsModel(unittest.TestCase):
    """Example Test Class"""

    class TestModel(SlimsBaseModel, validate_assignment=True):
        """Test case"""

        datefield: datetime = None
        stringfield: str = None
        quantfield: Annotated[float, UnitSpec("um", "nm")] = None

    def test_string_field(self):
        """Test basic usage for SLIMS column to Model field"""
        obj = self.TestModel()
        obj.stringfield = Column(
            {
                "datatype": "STRING",
                "name": "stringfield",
                "value": "value",
            }
        )

        self.assertEqual(obj.stringfield, "value")

    def test_quantity_field_context(self):
        """Test validation/serialization of a quantity type, with unit"""
        obj = self.TestModel()
        obj.quantfield = Column(
            {
                "datatype": "QUANTITY",
                "name": "quantfield",
                "value": 28.28,
                "unit": "um",
            }
        )

        self.assertEqual(obj.quantfield, 28.28)

        serialized = obj.model_dump(context="slims_post")["quantfield"]
        expected = {"amount": 28.28, "unit_display": "um"}

        self.assertEqual(serialized, expected)

    def test_quantity_field_no_context(self):
        """Test validation/serialization of a quantity type without unit"""
        obj = self.TestModel()
        obj.quantfield = Column(
            {
                "datatype": "QUANTITY",
                "name": "quantfield",
                "value": 28.28,
                "unit": "um",
            }
        )

        self.assertEqual(obj.quantfield, 28.28)

        serialized = obj.model_dump()["quantfield"]

        self.assertEqual(serialized, 28.28)

    def test_quantity_wrong_unit(self):
        """Ensure you get an error with an unexpected unit"""
        obj = self.TestModel()
        with self.assertRaises(ValueError):
            obj.quantfield = Column(
                {
                    "datatype": "QUANTITY",
                    "name": "quantfield",
                    "value": 28.28,
                    "unit": "erg",
                }
            )

    def test_alias(self):
        """Test aliasing of fields"""

        class TestModelAlias(SlimsBaseModel):
            """model with field aliases"""

            field: str = Field(
                ...,
                serialization_alias="alias",
                validation_alias="alias",
            )
            pk: Optional[int] = Field(
                None,
                serialization_alias="cntn_pk",
                validation_alias="cntn_pk",
            )

        record = Record(
            json_entity={
                "columns": [
                    {
                        "datatype": "STRING",
                        "name": "alias",
                        "value": "value",
                    },
                    {
                        "datatype": "INTEGER",
                        "name": "cntn_pk",
                        "value": 1,
                    },
                ]
            },
            slims_api=None,
        )
        obj = TestModelAlias.model_validate(record)

        self.assertEqual(obj.field, "value")
        obj.field = "value2"
        self.assertEqual(obj.field, "value2")
        serialized = obj.model_dump(include="field", by_alias=True)
        expected = {"alias": "value2"}
        self.assertEqual(serialized, expected)

    def test_unitspec(self):
        """Test unitspec with no arguments"""
        self.assertRaises(ValueError, UnitSpec)


if __name__ == "__main__":
    unittest.main()
