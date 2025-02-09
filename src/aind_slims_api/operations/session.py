"""
Module to get ExperimentRun (session) information for a mouse.
"""
from typing import Dict, List

from slims.slims import Slims
from slims.criteria import conjunction, equals, is_one_of
from sqlmodel import SQLModel
from aind_slims_api.tables.core import get_value_or_none, records_to_models
from aind_slims_api.tables.experiment_run_step import ExperimentRunStep
from aind_slims_api.tables.experiment_run_step_content import ExperimentRunStepContent
from aind_slims_api.tables.reference_data_record import ReferenceDataRecord
from aind_slims_api.tables.result import Result
from aind_slims_api.tables.content import Content


def get_ephys_session_info(client: Slims, labtracks_id: str) -> Dict[str, List[SQLModel]]:
    """
    Pulls session info from SLIMS for a mouse with the given labtracks_id. This would
    be simpler if the labtracks_id was a column in every relevant table.
    Parameters
    ----------
    client : Slims
    labtracks_id : str
    Returns
    -------
    Dict[str, List[SQLModel]]
      A dictionary with keys for Slims table names and the rows from that table.
    """
    if len(labtracks_id) == 0:
        raise ValueError(f"labtracks_id cannot be empty!")

    # Get mouse record from Content table to get record pk
    mouse_fetch_criteria = (
        conjunction()
            .add(equals("cntp_name", "Mouse"))
            .add(equals("cntn_barCode", labtracks_id))
    )
    cntn_recs = client.fetch(
        table="Content",
        criteria=mouse_fetch_criteria,
        sort=["-cntn_createdOn"],
        start=0,
        end=1
    )
    if len(cntn_recs) == 0:
        return dict()

    mouse_pk = cntn_recs[0].pk()

    # Get records from ExperimentRunStepContent table for mouse pk filtered by xprs_names
    exp_run_step_cntn_fetch_criteria = equals('xrsc_fk_content', mouse_pk)
    exp_run_step_content_recs = client.fetch(
        table="ExperimentRunStepContent",
        criteria=exp_run_step_cntn_fetch_criteria,
    )

    if len(exp_run_step_content_recs) == 0:
        return dict()
    # Get records from ExperimentRunStep table associated with exp_run_step_content records
    # There should be a value for xrsc_fk_experimentRunStep for each record.
    exp_run_step_pks = set()
    for record in exp_run_step_content_recs:
        if get_value_or_none(record, "xrsc_fk_experimentRunStep") is not None:
            exp_run_step_pks.add(get_value_or_none(record, "xrsc_fk_experimentRunStep"))
    exp_run_step_fetch_criteria = conjunction().add(is_one_of("xprn_pk", list(exp_run_step_pks))).add(
    is_one_of("xprs_name", ["Group of Sessions", "Mouse Session"])
)
    exp_run_step_recs = client.fetch(
        table="ExperimentRunStep",
        criteria=exp_run_step_fetch_criteria,
    )

    # Get records from Results table associated with mouse pk
    results_fetch_criteria = conjunction().add(
        equals('rslt_fk_content', mouse_pk)
    ).add(
        is_one_of(
            "test_name",
            [
                "test_session_information",
                "test_stimulus_epochs",
                "test_ephys_in_vivo_recording_stream"
            ]
        )
    )
    results = client.fetch("Result", criteria=results_fetch_criteria)

    # Get first round of ReferenceDataRecord primary keys from previous tables,
    # which includes Instrument, RewardDelivery, and Streams info.
    instrument_pks = set()
    inj_materials_pks = list()
    reward_del_pks = set()
    for exp_run_step_rec in exp_run_step_recs:
        inst_pk = get_value_or_none(exp_run_step_rec,
                                    "xprs_cf_fk_instrumentJson")
        if inst_pk is not None:
            instrument_pks.add(inst_pk)

    for result in results:
        inj_mat_pks = get_value_or_none(result,
                                        "rslt_cf_fk_injectionMaterial2")
        reward_delivery_pk = get_value_or_none(result,
                                               "rslt_cf_fk_rewardDelivery")
        if inj_mat_pks is not None:
            inj_materials_pks.extend(inj_mat_pks)
        if reward_delivery_pk:
            reward_del_pks.add(reward_delivery_pk)

    first_set_of_rdrc_pks = set(inj_materials_pks).union(reward_del_pks).union(instrument_pks)

    if not first_set_of_rdrc_pks:
        reference_data_records = []
    else:
        first_rdr_fetch_criteria = is_one_of(
            "rdrc_pk", list(first_set_of_rdrc_pks)
        )
        reference_data_records = client.fetch(
            "ReferenceDataRecord", criteria=first_rdr_fetch_criteria
        )

    # Get first round of ReferenceDataRecord primary keys associated with
    # previous ReferenceDataRecord records. We need primary and secondary targeted
    # structures and reward spouts.
    prim_targ_struct_pks = set()
    sec_targ_struct_pks = list()
    reward_spts_pks = set()
    for reference_data_record in reference_data_records:
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

    second_rdc_pks = set(sec_targ_struct_pks).union(prim_targ_struct_pks).union(
        reward_spts_pks)

    if not second_rdc_pks:
        second_reference_data_records = []
    else:
        second_rdr_fetch_criteria = is_one_of(
            "rdrc_pk", list(second_rdc_pks)
        )
        second_reference_data_records = client.fetch(
            "ReferenceDataRecord", criteria=second_rdr_fetch_criteria
        )

    reference_data_records.extend(second_reference_data_records)

    # Convert Records to SQLModels. Maybe this isn't needed
    content_models = records_to_models(records=cntn_recs, model=Content)
    exp_run_step_content_models = records_to_models(records=exp_run_step_content_recs, model=ExperimentRunStepContent)
    exp_run_step_models = records_to_models(records=exp_run_step_recs, model=ExperimentRunStep)
    results_models = records_to_models(records=results, model=Result)
    reference_data_record_models = records_to_models(records=reference_data_records, model=ReferenceDataRecord)

    return {
        Content.__tablename__: content_models,
        ExperimentRunStep.__tablename__: exp_run_step_models,
        ExperimentRunStepContent.__tablename__: exp_run_step_content_models,
        Result.__tablename__: results_models,
        ReferenceDataRecord.__tablename__: reference_data_record_models
    }
