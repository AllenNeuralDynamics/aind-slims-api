"""
Module to get ExperimentRun (session) information for a little mouse.
"""

from typing import Dict, List

from slims.criteria import conjunction, equals, is_one_of
from slims.internal import Record
from slims.slims import Slims
from sqlmodel import SQLModel

from aind_slims_api.tables.content import Content
from aind_slims_api.tables.core import get_value_or_none, records_to_models
from aind_slims_api.tables.experiment_run_step import ExperimentRunStep
from aind_slims_api.tables.experiment_run_step_content import ExperimentRunStepContent
from aind_slims_api.tables.reference_data_record import ReferenceDataRecord
from aind_slims_api.tables.result import Result


class SlimsApiHandler:
    """Handles SLIMS client."""

    def __init__(self, client: Slims):
        """Initialize class"""
        self.client = client

    def _get_content_rows(self, labtracks_id: str) -> List[Record]:
        """
        Get Records from Content table for labtracks_id.
        Parameters
        ----------
        labtracks_id : str

        Returns
        -------
        List[Record]

        Raises
        ------
        ValueError if labtracks_id is empty
        """
        if len(labtracks_id) == 0:
            raise ValueError("labtracks_id cannot be empty!")

        # Get mouse record from Content table to get record pk
        mouse_fetch_criteria = (
            conjunction()
            .add(equals("cntp_name", "Mouse"))
            .add(equals("cntn_barCode", labtracks_id))
        )
        cntn_recs = self.client.fetch(
            table="Content",
            criteria=mouse_fetch_criteria,
            sort=["-cntn_createdOn"],
            start=0,
            end=1,
        )
        return cntn_recs

    def _get_experiment_run_step_content_rows(
        self, content_recs: List[Record]
    ) -> List[Record]:
        """
        Get records from ExperimentRunStepContent table for xrsc_fk_content id.
        Parameters
        ----------
        content_recs : List[Record]

        Returns
        -------
        List[Record]

        """
        if len(content_recs) == 0:
            exp_run_step_content_recs = []
        else:
            xrsc_fk_content = content_recs[0].pk()
            exp_run_step_cntn_fetch_criteria = equals(
                "xrsc_fk_content", xrsc_fk_content
            )
            exp_run_step_content_recs = self.client.fetch(
                table="ExperimentRunStepContent",
                criteria=exp_run_step_cntn_fetch_criteria,
            )
        return exp_run_step_content_recs

    def _get_first_experiment_run_step_rows(
        self, exp_run_step_content_recs: List[Record]
    ) -> List[Record]:
        """
        Get records from ExperimentRunStep table associated with exp_run_step_content
        records. There should be a value for xrsc_fk_experimentRunStep for each record.
        Parameters
        ----------
        exp_run_step_content_recs : List[Record]

        Returns
        -------
        List[Record]

        """
        exp_run_step_pks = set()
        for record in exp_run_step_content_recs:
            if get_value_or_none(record, "xrsc_fk_experimentRunStep") is not None:
                exp_run_step_pks.add(
                    get_value_or_none(record, "xrsc_fk_experimentRunStep")
                )
        exp_run_step_fetch_criteria = is_one_of("xprs_pk", list(exp_run_step_pks))
        if exp_run_step_pks:
            exp_run_step_recs = self.client.fetch(
                table="ExperimentRunStep",
                criteria=exp_run_step_fetch_criteria,
            )
        else:
            exp_run_step_recs = []
        return exp_run_step_recs

    def _get_second_experiment_run_step_rows(
        self, exp_run_step_recs: List[Record]
    ) -> List[Record]:
        """
        Get records from ExperimentRunStep table associated with exp_run_step_content
        records. There should be a value for xrsc_fk_experimentRunStep for each record.
        Parameters
        ----------
        exp_run_step_recs : List[Record]

        Returns
        -------
        List[Record]

        """
        exp_run_pks = set()
        for record in exp_run_step_recs:
            if get_value_or_none(record, "xprs_fk_experimentRun") is not None:
                exp_run_pks.add(get_value_or_none(record, "xprs_fk_experimentRun"))
        exp_run_step_fetch_criteria = (
            conjunction()
            .add(is_one_of("xprs_fk_experimentRun", list(exp_run_pks)))
            .add(is_one_of("xprs_name", ["Group of Sessions", "Mouse Session"]))
        )
        if exp_run_pks:
            exp_run_step_recs = self.client.fetch(
                table="ExperimentRunStep",
                criteria=exp_run_step_fetch_criteria,
            )
        else:
            exp_run_step_recs = []
        return exp_run_step_recs

    def _get_first_results_rows(self, exp_run_step_recs: List[Record]) -> List[Record]:
        """
        Get records from Result table for exp_run_step_recs.
        Parameters
        ----------
        exp_run_step_recs : List[Record]

        Returns
        -------
        List[Record]

        """

        exp_run_step_rec_pks = set()
        for r in exp_run_step_recs:
            if get_value_or_none(r, "xprs_name") == "Mouse Session":
                exp_run_step_rec_pks.add(r.pk())

        results_fetch_criteria = (
            conjunction()
            .add(is_one_of("rslt_fk_experimentRunStep", list(exp_run_step_rec_pks)))
            .add(
                is_one_of(
                    "test_name",
                    ["test_session_information"],
                )
            )
        )
        if len(exp_run_step_rec_pks) > 0:
            results = self.client.fetch("Result", criteria=results_fetch_criteria)
        else:
            results = []
        return results

    def _get_second_results_rows(self, first_result_recs: List[Record]) -> List[Record]:
        """
        Get records from Result table from first set of Results.
        Parameters
        ----------
        first_result_recs : List[Record]

        Returns
        -------
        List[Record]

        """

        session_pks = set()
        for r in first_result_recs:
            session_pks.add(r.pk())

        results_fetch_criteria = (
            conjunction()
            .add(is_one_of("rslt_cf_fk_mouseSession", list(session_pks)))
            .add(
                is_one_of(
                    "test_name",
                    [
                        "test_stimulus_epochs",
                        "test_ephys_in_vivo_recording_stream",
                    ],
                )
            )
        )
        if len(session_pks) > 0:
            results = self.client.fetch("Result", criteria=results_fetch_criteria)
        else:
            results = []
        return results

    def _get_first_set_of_reference_data_records(
        self, exp_run_step_recs: List[Record], results: List[Record]
    ) -> List[Record]:
        """
        Get records from ReferenceDataRecord table for rslt_fk_content id,
        which includes Instrument, RewardDelivery, and Streams info.
        Parameters
        ----------
        exp_run_step_recs : List[Record]
        results : List[Record]
        Returns
        -------
        List[Record]

        """
        instrument_pks = set()
        inj_materials_pks = list()
        reward_del_pks = set()
        for exp_run_step_rec in exp_run_step_recs:
            inst_pk = get_value_or_none(exp_run_step_rec, "xprs_cf_fk_instrumentJson")
            if (
                inst_pk is not None
                and get_value_or_none(exp_run_step_rec, "xprs_name")
                == "Group of Sessions"
            ):
                instrument_pks.add(inst_pk)

        for result in results:
            inj_mat_pks = get_value_or_none(result, "rslt_cf_fk_injectionMaterial2")
            reward_delivery_pk = get_value_or_none(result, "rslt_cf_fk_rewardDelivery")
            if inj_mat_pks is not None:
                inj_materials_pks.extend(inj_mat_pks)
            if reward_delivery_pk:
                reward_del_pks.add(reward_delivery_pk)

        first_set_of_rdrc_pks = (
            set(inj_materials_pks).union(reward_del_pks).union(instrument_pks)
        )

        if not first_set_of_rdrc_pks:
            reference_data_records = []
        else:
            first_rdr_fetch_criteria = is_one_of("rdrc_pk", list(first_set_of_rdrc_pks))
            reference_data_records = self.client.fetch(
                "ReferenceDataRecord", criteria=first_rdr_fetch_criteria
            )
        return reference_data_records

    def _get_second_set_of_reference_data_records(
        self, first_set_of_reference_data_records: List[Record]
    ) -> List[Record]:
        """
        Get second round of ReferenceDataRecord primary keys associated with
        previous ReferenceDataRecord records. We need primary and secondary
        targeted structures and reward spouts.
        Parameters
        ----------
        first_set_of_reference_data_records : List[Record]

        Returns
        -------
        List[Record]

        """
        prim_targ_struct_pks = set()
        sec_targ_struct_pks = list()
        reward_spts_pks = set()
        for reference_data_record in first_set_of_reference_data_records:
            prim_targ_struct_pk = get_value_or_none(
                reference_data_record, "rdrc_cf_fk_primaryTargetedStructure"
            )
            reward_spout_pk = get_value_or_none(
                reference_data_record, "rdrc_cf_fk_rewardSpouts"
            )
            sec_targ_struct_pk_list = get_value_or_none(
                reference_data_record, "rdrc_cf_fk_secondaryTargetedStructures2"
            )
            if prim_targ_struct_pk is not None:
                prim_targ_struct_pks.add(prim_targ_struct_pk)
            if reward_spout_pk is not None:
                reward_spts_pks.add(reward_spout_pk)
            if sec_targ_struct_pk_list is not None:
                sec_targ_struct_pks.extend(sec_targ_struct_pk_list)

        second_rdc_pks = (
            set(sec_targ_struct_pks).union(prim_targ_struct_pks).union(reward_spts_pks)
        )

        if not second_rdc_pks:
            second_reference_data_records = []
        else:
            second_rdr_fetch_criteria = is_one_of("rdrc_pk", list(second_rdc_pks))
            second_reference_data_records = self.client.fetch(
                "ReferenceDataRecord", criteria=second_rdr_fetch_criteria
            )
        return second_reference_data_records

    def get_ephys_session_info(self, labtracks_id: str) -> Dict[str, List[SQLModel]]:
        """
        Pulls session info from SLIMS for a mouse with the given labtracks_id. This
        would be simpler if the labtracks_id was a column in every relevant table.
        Parameters
        ----------
        labtracks_id : str
        Returns
        -------
        Dict[str, List[SQLModel]]
          A dictionary with keys for Slims table names and the rows from that table.
        """
        content_records = self._get_content_rows(labtracks_id=labtracks_id)
        exp_run_step_content_recs = self._get_experiment_run_step_content_rows(
            content_recs=content_records
        )
        exp_run_step_recs_1 = self._get_first_experiment_run_step_rows(
            exp_run_step_content_recs=exp_run_step_content_recs
        )
        exp_run_step_recs_2 = self._get_second_experiment_run_step_rows(
            exp_run_step_recs=exp_run_step_recs_1
        )
        first_results = self._get_first_results_rows(
            exp_run_step_recs=exp_run_step_recs_2
        )
        second_results = self._get_second_results_rows(first_result_recs=first_results)
        first_set_of_rdrc = self._get_first_set_of_reference_data_records(
            results=second_results, exp_run_step_recs=exp_run_step_recs_2
        )
        second_set_of_rdrc = self._get_second_set_of_reference_data_records(
            first_set_of_reference_data_records=first_set_of_rdrc
        )
        exp_run_step_recs = exp_run_step_recs_1 + exp_run_step_recs_2
        reference_data_records = first_set_of_rdrc + second_set_of_rdrc
        results = first_results + second_results
        # Convert Records to SQLModels. Maybe this isn't needed and we can just
        # return the Record objects directly.
        content_models = records_to_models(records=content_records, model=Content)
        exp_run_step_content_models = records_to_models(
            records=exp_run_step_content_recs, model=ExperimentRunStepContent
        )
        exp_run_step_models = records_to_models(
            records=exp_run_step_recs, model=ExperimentRunStep
        )
        results_models = records_to_models(records=results, model=Result)
        reference_data_record_models = records_to_models(
            records=reference_data_records, model=ReferenceDataRecord
        )
        return {
            Content.__tablename__: content_models,
            ExperimentRunStep.__tablename__: exp_run_step_models,
            ExperimentRunStepContent.__tablename__: exp_run_step_content_models,
            Result.__tablename__: results_models,
            ReferenceDataRecord.__tablename__: reference_data_record_models,
        }
