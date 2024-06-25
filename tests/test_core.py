""" Tests methods in core module"""

import json
import os
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.criteria import conjunction, equals
from slims.internal import Record, _SlimsApiException

from aind_slims_api.core import SlimsClient
from aind_slims_api.unit import SlimsUnit

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestSlimsClient(unittest.TestCase):
    """Tests methods in SlimsClient class"""

    @classmethod
    def setUpClass(cls):
        """Sets up class by downloading responses"""
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_client = example_client

        def get_response(attribute_name: str):
            """Utility method to download json file with {attribute_name}.json
            from resource dir"""
            with open(
                os.path.join(str(RESOURCES_DIR), f"{attribute_name}.json"), "r"
            ) as f:
                response = [
                    Record(json_entity=r, slims_api=example_client.db.slims_api)
                    for r in json.load(f)
                ]
            return response

        cls.example_fetch_unit_response = get_response("example_fetch_unit_response")
        cls.example_fetch_mouse_response = get_response("example_fetch_mouse_response")
        cls.example_fetch_user_response = get_response("example_fetch_user_response")

    def test_rest_link(self):
        """Tests rest_link method with both queries and no queries."""

        rest_link_no_queries = self.example_client.rest_link(table="Content")
        rest_link_with_queries = self.example_client.rest_link(
            table="Content", **{"limit": 1, "start": 0}
        )
        self.assertEqual("http://fake_url/rest/Content", rest_link_no_queries)
        self.assertEqual(
            "http://fake_url/rest/Content?limit=1?start=0", rest_link_with_queries
        )

    @patch("slims.slims.Slims.fetch")
    def test_fetch(self, mock_slims_fetch: MagicMock):
        """Tests fetch method success"""
        mock_slims_fetch.return_value = self.example_fetch_unit_response
        response = self.example_client.fetch(table="Unit", start=0, end=2)
        self.assertEqual(self.example_fetch_unit_response, response)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_with_criteria(self, mock_slims_fetch: MagicMock):
        """Tests fetch method constructs criteria correctly"""
        mock_slims_fetch.return_value = self.example_fetch_mouse_response
        response = self.example_client.fetch(
            "Content",
            equals("cntn_barCode", "123456"),
            cntp_name="Mouse",
        )
        expected_criteria = (
            conjunction()
            .add(equals("cntn_barCode", "123456"))
            .add(equals("cntp_name", "Mouse"))
        )
        actual_criteria = mock_slims_fetch.mock_calls[0].args[1]
        self.assertEqual(expected_criteria.to_dict(), actual_criteria.to_dict())
        self.assertEqual(self.example_fetch_mouse_response, response)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_error(self, mock_slims_fetch: MagicMock):
        """Tests fetch method when a _SlimsApiException is raised"""
        mock_slims_fetch.side_effect = _SlimsApiException("Something went wrong")
        with self.assertRaises(_SlimsApiException) as e:
            self.example_client.fetch(
                "Content",
                cntp_name="Mouse",
            )
        self.assertEqual("Something went wrong", e.exception.args[0])

    @patch("slims.slims.Slims.fetch")
    def test_fetch_user(self, mock_slims_fetch: MagicMock):
        """Tests fetch_user method"""
        mock_slims_fetch.return_value = self.example_fetch_user_response
        response = self.example_client.fetch_user(user_name="PersonA")
        self.assertEqual(self.example_fetch_user_response, response)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_pk(self, mock_slims_fetch: MagicMock):
        """Tests fetch_pk method when several records are returned"""
        # Use this example_client since result is cached
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        mock_slims_fetch.return_value = self.example_fetch_unit_response
        pk = example_client.fetch_pk(table="Unit")
        self.assertEqual(31, pk)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_pk_none(self, mock_slims_fetch: MagicMock):
        """Tests fetch_pk method when no records are returned"""
        # Use this example_client since result is cached
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        mock_slims_fetch.return_value = []
        pk = example_client.fetch_pk(table="Content")
        self.assertIsNone(pk)

    @patch("logging.Logger.info")
    @patch("slims.slims.Slims.add")
    def test_add(self, mock_slims_add: MagicMock, mock_log: MagicMock):
        """Tests add method"""
        mock_slims_add.return_value = self.example_fetch_unit_response[0]
        input_data = deepcopy(self.example_fetch_unit_response[0].json_entity)
        record = self.example_client.add(table="Unit", data=input_data)
        self.assertEqual(self.example_fetch_unit_response[0], record)
        mock_log.assert_called_once_with("SLIMS Add: Unit/31")

    @patch("slims.slims.Slims.fetch_by_pk")
    @patch("logging.Logger.info")
    @patch("slims.internal.Record.update")
    def test_update(
        self,
        mock_update: MagicMock,
        mock_log: MagicMock,
        mock_fetch_by_pk: MagicMock,
    ):
        """Tests update method success"""
        input_data = deepcopy(self.example_fetch_unit_response[0].json_entity)
        mock_record = Record(
            json_entity=input_data, slims_api=self.example_client.db.slims_api
        )
        mock_fetch_by_pk.return_value = mock_record
        new_data = deepcopy(input_data)
        new_data["columns"][0]["value"] = "PM^3"
        mocked_updated_record = Record(
            json_entity=new_data, slims_api=self.example_client.db.slims_api
        )
        mock_update.return_value = mocked_updated_record
        new_record = self.example_client.update(table="Unit", pk=31, data=new_data)
        self.assertEqual(mocked_updated_record, new_record)
        mock_log.assert_called_once_with("SLIMS Update: Unit/31")

    @patch("slims.slims.Slims.fetch_by_pk")
    @patch("logging.Logger.info")
    @patch("slims.internal.Record.update")
    def test_update_failure(
        self,
        mock_update: MagicMock,
        mock_log: MagicMock,
        mock_fetch_by_pk: MagicMock,
    ):
        """Tests update method when a failure occurs"""
        mock_fetch_by_pk.return_value = None
        with self.assertRaises(ValueError) as e:
            self.example_client.update(table="Unit", pk=30000, data={})
        self.assertEqual(
            'No data in SLIMS "Unit" table for pk "30000"',
            e.exception.args[0],
        )
        mock_update.assert_not_called()
        mock_log.assert_not_called()

    @patch("logging.Logger.info")
    @patch("slims.slims.Slims.add")
    def test_add_model(self, mock_slims_add: MagicMock, mock_log: MagicMock):
        """Tests add_model method with mock mouse data"""
        record = self.example_fetch_unit_response[0]
        mock_slims_add.return_value = record
        input_model = SlimsUnit.model_validate(record)
        added = self.example_client.add_model(input_model)
        self.assertEqual(input_model, added)
        mock_log.assert_called_once_with("SLIMS Add: Unit/31")

    @patch("slims.slims.Slims.fetch_by_pk")
    @patch("logging.Logger.info")
    @patch("slims.internal.Record.update")
    def test_update_model(
        self,
        mock_update: MagicMock,
        mock_log: MagicMock,
        mock_fetch_by_pk: MagicMock,
    ):
        """Tests update method success"""
        input_data = deepcopy(self.example_fetch_unit_response[0].json_entity)
        mock_record = Record(
            json_entity=input_data, slims_api=self.example_client.db.slims_api
        )
        mock_fetch_by_pk.return_value = mock_record
        updated_model = SlimsUnit.model_validate(mock_record)
        new_data = deepcopy(input_data)
        new_data["columns"][0]["value"] = "PM^3"
        mocked_updated_record = Record(
            json_entity=new_data, slims_api=self.example_client.db.slims_api
        )
        mock_update.return_value = mocked_updated_record
        updated_model = SlimsUnit.model_validate(mocked_updated_record)
        returned_model = self.example_client.update_model(updated_model)
        self.assertEqual(updated_model, returned_model)
        mock_log.assert_called_once_with("SLIMS Update: Unit/31")


if __name__ == "__main__":
    unittest.main()
