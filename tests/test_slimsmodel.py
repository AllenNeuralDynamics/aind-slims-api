""" Tests the generic SlimsBaseModel"""

from datetime import datetime
from typing import Annotated
import unittest

from pydantic import Field
from slims.internal import Record, Column

from aind_slims_api.core import SlimsBaseModel, UnitSpec


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

    def test_quantity_field(self):
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

        serialized = obj.model_dump()["quantfield"]
        expected = {"amount": 28.28, "unit_display": "um"}

        self.assertEqual(serialized, expected)

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

            field: str = Field(..., alias="alias")
            pk: int = Field(None, alias="cntn_pk")

        record = Record(
            json_entity={
                "columns": [
                    {
                        "datatype": "STRING",
                        "name": "alias",
                        "value": "value",
                    }
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
