""" Tests methods in core module"""

import json
import os
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

from requests import Response
from slims.criteria import conjunction, equals, is_one_of
from slims.internal import Record, _SlimsApiException

from aind_slims_api.core import SlimsAttachment, SlimsClient
from aind_slims_api.exceptions import SlimsRecordNotFound
from aind_slims_api.models.behavior_session import SlimsBehaviorSession
from aind_slims_api.models.unit import SlimsUnit
from aind_slims_api.models.user import SlimsUser

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestSlimsClient(unittest.TestCase):
    """Tests methods in SlimsClient class"""

    example_client: SlimsClient
    example_fetch_unit_response: list[Record]
    example_fetch_mouse_response: list[Record]
    example_fetch_user_response: list[Record]
    example_fetch_attachment_response: list[Record]
    example_add_attachments_response_text: str

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
        cls.example_fetch_attachment_response = get_response(
            "example_fetch_attachments_response.json_entity"
        )
        cls.example_add_attachments_response_text = (
            RESOURCES_DIR / "example_add_attachment_content_response_text.txt"
        ).read_text()

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
            cntp_name=["Mouse", "Rat"],
        )
        expected_criteria = (
            conjunction()
            .add(equals("cntn_barCode", "123456"))
            .add(is_one_of("cntp_name", ["Mouse", "Rat"]))
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

    @patch("slims.slims.Slims.fetch_by_pk")
    @patch("logging.Logger.info")
    @patch("slims.internal.Record.update")
    def test_update_model_no_pk(
        self,
        mock_update: MagicMock,
        mock_log: MagicMock,
        mock_fetch_by_pk: MagicMock,
    ):
        """Tests update method when a failure occurs"""
        mock_fetch_by_pk.return_value = None
        with self.assertRaises(ValueError):
            self.example_client.update_model(SlimsUnit.model_construct(pk=None))
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

    @patch("slims.slims.Slims.fetch")
    def test_fetch_model_no_records(self, mock_slims_fetch: MagicMock):
        """Tests fetch_user method"""
        mock_slims_fetch.return_value = []
        with self.assertRaises(SlimsRecordNotFound):
            self.example_client.fetch_model(SlimsUnit)

    @patch("slims.internal._SlimsApi.get_entities")
    def test_fetch_attachments(self, mock_get_entities: MagicMock):
        """Tests fetch_attachments method success."""
        # slims_api is dynamically added to slims client
        mock_get_entities.return_value = self.example_fetch_attachment_response
        unit = SlimsUnit.model_validate(
            Record(
                json_entity=self.example_fetch_unit_response[0].json_entity,
                slims_api=self.example_client.db.slims_api,
            )
        )
        attachments = self.example_client.fetch_attachments(
            unit,
        )
        self.assertEqual(1, len(attachments))

    @patch("slims.slims._SlimsApi.get")
    def test_fetch_attachment_content(self, mock_get: MagicMock):
        """Tests fetch_attachment_content method success."""
        mock_get.return_value = Response()
        self.example_client.fetch_attachment_content(
            SlimsAttachment(
                attm_name="test",
                attm_pk=1,
            )
        )
        mock_get.assert_called_once()

    @patch("slims.internal._SlimsApi.post")
    def test_add_attachment_content(self, mock_post: MagicMock):
        """Tests add_attachment_content method success."""
        mock_response = MagicMock()
        mock_response.text = self.example_add_attachments_response_text
        mock_post.return_value = mock_response
        unit_pk = 1
        result = self.example_client.add_attachment_content(
            SlimsUnit(
                unit_name="test",
                unit_pk=unit_pk,
            ),
            "test",
            "some test content",
        )
        self.assertEqual(result, int(self.example_add_attachments_response_text))
        self.assertEqual(mock_post.call_count, 1)
        self.assertEqual(
            mock_post.mock_calls[0].kwargs["body"]["atln_recordPk"], unit_pk
        )

    @patch("slims.internal._SlimsApi.post")
    def test_add_attachment_content_no_pk(self, mock_post: MagicMock):
        """Tests add_attachment_content method failure due to lack of pk."""
        mock_response = MagicMock()
        mock_response.text.return_value = self.example_add_attachments_response_text
        mock_post.return_value = mock_response
        with self.assertRaises(ValueError):
            self.example_client.add_attachment_content(
                SlimsBehaviorSession(),
                "test",
                "some test content",
            )
        mock_post.assert_not_called()

    @patch("logging.Logger.error")
    def test__validate_model_invalid_model(self, mock_log: MagicMock):
        """Tests _validate_model method with one invalid model and one valid
        one.
        """
        valid_data = deepcopy(self.example_fetch_unit_response[0].json_entity)
        invalid_data = deepcopy(self.example_fetch_unit_response[0].json_entity)
        invalid_data["columns"][0]["value"] = 1
        validated = self.example_client._validate_models(
            SlimsUnit,
            [
                Record(
                    json_entity=valid_data,
                    slims_api=self.example_client.db.slims_api,
                ),
                Record(
                    json_entity=invalid_data,
                    slims_api=self.example_client.db.slims_api,
                ),
            ],
        )
        self.assertEqual(1, len(validated))
        self.assertEqual(1, mock_log.call_count)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_model_criterion(self, mock_slims_fetch: MagicMock):
        """Tests fetch_model method with a criterion."""
        mock_slims_fetch.return_value = self.example_fetch_user_response
        self.example_client.fetch_model(SlimsUser, equals("username", "LKim"))
        mock_slims_fetch.assert_called_once()

    @patch("slims.slims.Slims.fetch")
    def test_fetch_model_criterion_junction(self, mock_slims_fetch: MagicMock):
        """Tests fetch_model method with a junction criterion."""
        mock_slims_fetch.return_value = self.example_fetch_user_response
        self.example_client.fetch_model(
            SlimsUser,
            conjunction().add(equals("username", "LKim")),
        )
        mock_slims_fetch.assert_called_once()

    @patch("slims.slims.Slims.fetch")
    def test_fetch_model_criterion_invalid_criterion_type(
        self, mock_slims_fetch: MagicMock
    ):
        """Tests fetch_model method with an invalid criterion type."""
        mock_slims_fetch.return_value = []
        with self.assertRaises(ValueError):
            self.example_client.fetch_model(SlimsUser, equals("username", 1))
        mock_slims_fetch.assert_not_called()

    @patch("slims.internal._SlimsApi.get_entities")
    def test_fetch_attachment(self, mock_get_entities: MagicMock):
        """Tests fetch_attachment method success."""
        mock_get_entities.return_value = self.example_fetch_attachment_response
        unit = SlimsUnit.model_validate(
            Record(
                json_entity=self.example_fetch_unit_response[0].json_entity,
                slims_api=self.example_client.db.slims_api,
            )
        )
        self.example_client.fetch_attachment(unit, equals("name", "test"))

    @patch("slims.internal._SlimsApi.get_entities")
    def test_fetch_attachment_no_attachments(self, mock_get_entities: MagicMock):
        """Tests fetch_attachment method failure due to no attachments."""
        mock_get_entities.return_value = []
        unit = SlimsUnit.model_validate(
            Record(
                json_entity=self.example_fetch_unit_response[0].json_entity,
                slims_api=self.example_client.db.slims_api,
            )
        )
        with self.assertRaises(SlimsRecordNotFound):
            self.example_client.fetch_attachment(unit)

    @patch("slims.slims.Slims.fetch")
    def test_fetch_str_sort(self, mock_slims_fetch: MagicMock):
        """Tests fetch method when sort is a string."""
        mock_slims_fetch.return_value = []
        self.example_client.fetch(SlimsUser._slims_table, sort="username")
        mock_slims_fetch.assert_called_once()

    @patch("slims.slims.Slims.fetch")
    def test_fetch_models_invalid_start_end(self, mock_slims_fetch: MagicMock):
        """Tests fetch_model method failure due to only supplying start or end."""
        mock_slims_fetch.return_value = []
        with self.assertRaises(ValueError):
            self.example_client.fetch_models(SlimsUser, start=1)
        with self.assertRaises(ValueError):
            self.example_client.fetch_models(SlimsUser, end=1)
        mock_slims_fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
