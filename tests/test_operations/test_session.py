"""Tests methods in session module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.operations.session import SlimsApiHandler

RESOURCES_DIR = (
    Path(os.path.dirname(os.path.realpath(__file__)))
    / ".."
    / "resources"
    / "operations"
)


class TestMethods(unittest.TestCase):
    """Tests methods in module."""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup class by preloading json files"""

        with open(RESOURCES_DIR / "content.json") as f:
            content = json.load(f)
        with open(RESOURCES_DIR / "experiment_run_step_1.json") as f:
            experiment_run_step_1 = json.load(f)
        with open(RESOURCES_DIR / "experiment_run_step_2.json") as f:
            experiment_run_step_2 = json.load(f)
        with open(RESOURCES_DIR / "experiment_run_step_content.json") as f:
            experiment_run_step_content = json.load(f)
        with open(RESOURCES_DIR / "reference_data_record_1.json") as f:
            reference_data_record_1 = json.load(f)
        with open(RESOURCES_DIR / "reference_data_record_2.json") as f:
            reference_data_record_2 = json.load(f)
        with open(RESOURCES_DIR / "result_1.json") as f:
            result_1 = json.load(f)
        with open(RESOURCES_DIR / "result_2.json") as f:
            result_2 = json.load(f)
        # noinspection PyTypeChecker
        cls.content_recs = [Record(json_entity=r, slims_api=None) for r in content]
        # noinspection PyTypeChecker
        cls.experiment_run_step_1_recs = [
            Record(json_entity=r, slims_api=None) for r in experiment_run_step_1
        ]
        # noinspection PyTypeChecker
        cls.experiment_run_step_2_recs = [
            Record(json_entity=r, slims_api=None) for r in experiment_run_step_2
        ]
        # noinspection PyTypeChecker
        cls.experiment_run_step_content_recs = [
            Record(json_entity=r, slims_api=None) for r in experiment_run_step_content
        ]
        # noinspection PyTypeChecker
        cls.reference_data_record_1_recs = [
            Record(json_entity=r, slims_api=None) for r in reference_data_record_1
        ]
        # noinspection PyTypeChecker
        cls.reference_data_record_2_recs = [
            Record(json_entity=r, slims_api=None) for r in reference_data_record_2
        ]
        # noinspection PyTypeChecker
        cls.result_1_recs = [Record(json_entity=r, slims_api=None) for r in result_1]
        # noinspection PyTypeChecker
        cls.result_2_recs = [Record(json_entity=r, slims_api=None) for r in result_2]

    @patch("slims.slims.Slims")
    def test_get_content_rows_bad_id(self, mock_slims: MagicMock):
        """Tests _get_content_rows when labtacks id is empty"""
        api_handler = SlimsApiHandler(client=mock_slims)
        with self.assertRaises(ValueError) as e:
            api_handler._get_content_rows(labtracks_id="")
        self.assertEqual("labtracks_id cannot be empty!", str(e.exception))

    @patch("slims.slims.Slims")
    def test_get_content_rows(self, mock_slims: MagicMock):
        """Tests _get_content_rows when labtacks id is good."""
        mock_slims.fetch.return_value = self.content_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_content_rows(labtracks_id="725804")
        self.assertEqual(3135, recs[0].pk())

    @patch("slims.slims.Slims")
    def test_get_experiment_run_step_content_rows(self, mock_slims: MagicMock):
        """Tests _get_experiment_run_step_content_rows."""
        mock_slims.fetch.return_value = self.experiment_run_step_content_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_experiment_run_step_content_rows(
            content_recs=self.content_recs
        )
        expected_call_arg = {
            "fieldName": "xrsc_fk_content",
            "operator": "equals",
            "value": 3135,
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(6, len(recs))

    @patch("slims.slims.Slims")
    def test_get_first_experiment_run_step_rows(self, mock_slims: MagicMock):
        """Tests _get_first_experiment_run_step_rows."""
        mock_slims.fetch.return_value = self.experiment_run_step_1_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_first_experiment_run_step_rows(
            exp_run_step_content_recs=self.experiment_run_step_content_recs
        )
        expected_call_arg = {
            "fieldName": "xprs_pk",
            "operator": "inSet",
            "value": [64452, 64454, 64459, 64238, 64241, 64246],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(6, len(recs))

    @patch("slims.slims.Slims")
    def test_get_second_experiment_run_step_rows(self, mock_slims: MagicMock):
        """Tests _get_second_experiment_run_step_rows."""
        mock_slims.fetch.return_value = self.experiment_run_step_2_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_second_experiment_run_step_rows(
            exp_run_step_recs=self.experiment_run_step_1_recs
        )
        expected_call_arg = {
            "operator": "and",
            "criteria": [
                {
                    "fieldName": "xprs_fk_experimentRun",
                    "operator": "inSet",
                    "value": [41057, 41058, 41059, 41011, 41012, 41013],
                },
                {
                    "fieldName": "xprs_name",
                    "operator": "inSet",
                    "value": ["Group of Sessions", "Mouse Session"],
                },
            ],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(6, len(recs))

    @patch("slims.slims.Slims")
    def test_get_first_results_rows(self, mock_slims: MagicMock):
        """Tests _get_first_results_rows."""
        mock_slims.fetch.return_value = self.result_1_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_first_results_rows(
            exp_run_step_recs=self.experiment_run_step_2_recs
        )
        expected_call_arg = {
            "operator": "and",
            "criteria": [
                {
                    "fieldName": "rslt_fk_experimentRunStep",
                    "operator": "inSet",
                    "value": [64248, 64243, 64456],
                },
                {
                    "fieldName": "test_name",
                    "operator": "inSet",
                    "value": ["test_session_information"],
                },
            ],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(2, len(recs))

    @patch("slims.slims.Slims")
    def test_get_second_results_rows(self, mock_slims: MagicMock):
        """Tests _get_second_results_rows."""
        mock_slims.fetch.return_value = self.result_2_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_second_results_rows(
            first_result_recs=self.result_1_recs
        )
        expected_call_arg = {
            "operator": "and",
            "criteria": [
                {
                    "fieldName": "rslt_cf_fk_mouseSession",
                    "operator": "inSet",
                    "value": [2329, 2266],
                },
                {
                    "fieldName": "test_name",
                    "operator": "inSet",
                    "value": [
                        "test_stimulus_epochs",
                        "test_ephys_in_vivo_recording_stream",
                    ],
                },
            ],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(3, len(recs))

    @patch("slims.slims.Slims")
    def test_get_first_set_of_reference_data_records(self, mock_slims: MagicMock):
        """Tests _get_first_set_of_reference_data_records."""
        mock_slims.fetch.return_value = self.reference_data_record_1_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_first_set_of_reference_data_records(
            exp_run_step_recs=self.experiment_run_step_2_recs,
            results=self.result_2_recs,
        )
        expected_call_arg = {
            "fieldName": "rdrc_pk",
            "operator": "inSet",
            "value": [3419, 3352, 3418, 3355, 1743],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(5, len(recs))

    @patch("slims.slims.Slims")
    def test_get_second_set_of_reference_data_records(self, mock_slims: MagicMock):
        """Tests _get_second_set_of_reference_data_records."""
        mock_slims.fetch.return_value = self.reference_data_record_2_recs
        api_handler = SlimsApiHandler(client=mock_slims)
        recs = api_handler._get_second_set_of_reference_data_records(
            first_set_of_reference_data_records=self.reference_data_record_1_recs
        )
        expected_call_arg = {
            "fieldName": "rdrc_pk",
            "operator": "inSet",
            "value": [2742],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )
        self.assertEqual(1, len(recs))

    @patch("slims.slims.Slims")
    @patch("aind_slims_api.operations.session.SlimsApiHandler._get_content_rows")
    def test_get_session_info_empty(
        self, mock_get_content_rows: MagicMock, mock_slims: MagicMock
    ):
        """Tests get_session_info when the mouse isn't found."""
        mock_get_content_rows.return_value = []
        api_handler = SlimsApiHandler(client=mock_slims)
        session_info = api_handler.get_ephys_session_info(labtracks_id="0")
        expected_session_info = {
            "Content": [],
            "ExperimentRunStep": [],
            "ExperimentRunStepContent": [],
            "Result": [],
            "ReferenceDataRecord": [],
        }
        mock_slims.fetch.assert_not_called()
        self.assertEqual(expected_session_info, session_info)

    @patch("slims.slims.Slims")
    @patch("aind_slims_api.operations.session.SlimsApiHandler._get_content_rows")
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler"
        "._get_experiment_run_step_content_rows"
    )
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler"
        "._get_first_experiment_run_step_rows"
    )
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler"
        "._get_second_experiment_run_step_rows"
    )
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler" "._get_first_results_rows"
    )
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler" "._get_second_results_rows"
    )
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler"
        "._get_first_set_of_reference_data_records"
    )
    @patch(
        "aind_slims_api.operations.session.SlimsApiHandler"
        "._get_second_set_of_reference_data_records"
    )
    def test_get_session_info(
        self,
        mock_get_second_set_of_reference_data_records: MagicMock,
        mock_get_first_set_of_reference_data_records: MagicMock,
        mock_get_second_results_rows: MagicMock,
        mock_get_first_results_rows: MagicMock,
        mock_get_second_experiment_run_step_rows: MagicMock,
        mock_get_first_experiment_run_step_rows: MagicMock,
        mock_get_experiment_run_step_content_rows: MagicMock,
        mock_get_content_rows: MagicMock,
        mock_slims: MagicMock,
    ):
        """Tests get_session_info when the mouse is found."""
        mock_get_content_rows.return_value = self.content_recs
        mock_get_experiment_run_step_content_rows.return_value = (
            self.experiment_run_step_content_recs
        )
        mock_get_first_experiment_run_step_rows.return_value = (
            self.experiment_run_step_1_recs
        )
        mock_get_second_experiment_run_step_rows.return_value = (
            self.experiment_run_step_2_recs
        )
        mock_get_first_results_rows.return_value = self.result_1_recs
        mock_get_second_results_rows.return_value = self.result_2_recs
        mock_get_first_set_of_reference_data_records.return_value = (
            self.reference_data_record_1_recs
        )
        mock_get_second_set_of_reference_data_records.return_value = (
            self.reference_data_record_2_recs
        )

        api_handler = SlimsApiHandler(client=mock_slims)
        session_info = api_handler.get_ephys_session_info(labtracks_id="725804")
        mock_slims.fetch.assert_not_called()
        self.assertEqual(1, len(session_info["Content"]))
        self.assertEqual(12, len(session_info["ExperimentRunStep"]))
        self.assertEqual(6, len(session_info["ExperimentRunStepContent"]))
        self.assertEqual(5, len(session_info["Result"]))
        self.assertEqual(6, len(session_info["ReferenceDataRecord"]))

    @patch("slims.slims.Slims")
    def test_get_first_set_of_reference_data_records_edge_case(
        self, mock_slims: MagicMock
    ):
        """Tests _get_first_set_of_reference_data_records with reward pks."""
        # noinspection PyTypeChecker
        result_recs = [
            Record(
                json_entity={
                    "pk": 1743,
                    "tableName": "Result",
                    "columns": [
                        {
                            "datatype": "INTEGER",
                            "name": "rslt_cf_fk_rewardDelivery",
                            "title": "Name",
                            "position": 0,
                            "value": 1,
                            "hidden": False,
                            "editable": True,
                        }
                    ],
                },
                slims_api=None,
            )
        ]
        mock_slims.fetch.return_value = []
        api_handler = SlimsApiHandler(client=mock_slims)
        _ = api_handler._get_first_set_of_reference_data_records(
            exp_run_step_recs=self.experiment_run_step_2_recs,
            results=result_recs,
        )
        expected_call_arg = {
            "fieldName": "rdrc_pk",
            "operator": "inSet",
            "value": [3352, 1, 1743],
        }
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )

    @patch("slims.slims.Slims")
    def test_get_second_set_of_reference_data_records_edge_case(
        self, mock_slims: MagicMock
    ):
        """Tests _get_second_set_of_reference_data_records with rewards."""
        # noinspection PyTypeChecker
        first_recs = [
            Record(
                json_entity={
                    "pk": 1743,
                    "tableName": "ReferenceDataRecord",
                    "columns": [
                        {
                            "datatype": "INTEGER",
                            "name": "rdrc_cf_fk_rewardSpouts",
                            "title": "Name",
                            "position": 0,
                            "value": 1,
                            "hidden": False,
                            "editable": True,
                        }
                    ],
                },
                slims_api=None,
            )
        ]
        mock_slims.fetch.return_value = []
        api_handler = SlimsApiHandler(client=mock_slims)
        _ = api_handler._get_second_set_of_reference_data_records(
            first_set_of_reference_data_records=first_recs,
        )
        expected_call_arg = {"fieldName": "rdrc_pk", "operator": "inSet", "value": [1]}
        self.assertEqual(
            expected_call_arg,
            mock_slims.fetch.mock_calls[0].kwargs["criteria"].to_dict(),
        )


if __name__ == "__main__":
    unittest.main()
