"""Contains models for workflows stored in SLIMS."""

from datetime import datetime
from typing import Annotated, Optional, ClassVar, Any
from pydantic import Field
from aind_slims_api.models.utils import UnitSpec
from aind_slims_api.models.base import SlimsBaseModel


class SlimsExperimentRunStepContent(SlimsBaseModel):
    """Model for a SLIMS ExperimentRunStepContent"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="xrsc_pk", validation_alias="xrsc_pk"
    )
    mouse_pk: Optional[int] = Field(
        default=None,
        serialization_alias="xrsc_fk_content",
        validation_alias="xrsc_fk_content",
    )
    runstep_pk: Optional[int] = Field(
        default=None,
        serialization_alias="xrsc_fk_experimentRunStep",
        validation_alias="xrsc_fk_experimentRunStep",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="xrsc_createdOn",
        validation_alias="xrsc_createdOn",
    )
    _slims_table = "ExperimentRunStepContent"


class SlimsExperimentRunStep(SlimsBaseModel):
    """Model for a Slims ExperimentRunStep"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="xprs_pk", validation_alias="xprs_pk"
    )
    name: Optional[str] = Field(
        default=None, serialization_alias="xprs_name", validation_alias="xprs_name"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="xprs_createdOn",
        validation_alias="xprs_createdOn",
    )
    experimentrun_pk: Optional[int] = Field(
        default=None,
        serialization_alias="xprs_fk_experimentRun",
        validation_alias="xprs_fk_experimentRun",
    )
    experiment_template_pk: Optional[int] = Field(
        default=None,
        serialization_alias="xpst_fk_experimentTemplate",
        validation_alias="xpst_fk_experimentTemplate"
    )
    _slims_table = "ExperimentRunStep"

class SlimsExperimentTemplate(SlimsBaseModel):
    """Model for a Slims Experiment Template"""
    pk: Optional[int] = Field(
        default=None, serialization_alias="xptm_pk", validation_alias="xptm_pk"
    )
    name: Optional[str] = Field(
        default=None, serialization_alias="xptm_name", validation_alias="xptm_name"
    )
    version_name: Optional[str] = Field(
        default=None,
        serialization_alias="xptm_nameVersion",
        validation_alias="xptm_nameVersion"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="xptm_createdOn",
        validation_alias="xptm_createdOn",
    )
    _slims_table = "ExperimentTemplate"

class SlimsGroupOfSessionsRunStep(SlimsExperimentRunStep):
    """Model for a Slims ExperimentRunStep"""

    session_type: Optional[str] = Field(
        default=None,
        serialization_alias="xprs_cf_sessionType",
        validation_alias="xprs_cf_sessionType",
    )
    mouse_platform_name: Optional[str] = Field(
        default=None,
        serialization_alias="xprs_cf_mousePlatformName",
        validation_alias="xprs_cf_mousePlatformName",
    )
    active_mouse_platform: Optional[bool] = Field(
        default=None,
        serialization_alias="xprs_cf_activeMousePlatform",
        validation_alias="xprs_cf_activeMousePlatform",
    )
    instrument_pk: Optional[int] = Field(
        default=None,
        serialization_alias="xprs_cf_fk_instrumentJson",
        validation_alias="xprs_cf_fk_instrumentJson",
    )
    # TODO: add device calibrations once we have an example
    # device_calibrations_attachment: Optional[str] = Field(
    #     default=None,
    #     serialization_alias="xprs_cf_deviceCalibrations",
    #     validation_alias="xprs_cf_deviceCalibrations"
    # )
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "xprs_name": "Group of Sessions",
    }


class SlimsMouseSessionRunStep(SlimsExperimentRunStep):
    """Model for a Slims ExperimentRunStep"""

    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "xprs_name": "Mouse Session",
    }

class SlimsProtocolRunStep(SlimsExperimentRunStep):
    """Model for a Slims Protocol ExperimentRunStep"""

    protocol_pk: Optional[int] = Field(
        None,
        serialization_alias="xprs_cf_fk_protocol",
        validation_alias="xprs_cf_fk_protocol"
    )
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "xprs_name": "Protocol",
    }

class SlimsWashRunStep(SlimsExperimentRunStep):
    """Model for a Slims Wash ExperimentRunStep"""

    wash_name: Optional[str] = Field(
        None,
        serialization_alias="xprs_name",
        validation_alias="xprs_name"
    )
    spim_wash_type: Optional[str] = Field(
        None,
        serialization_alias="xprs_cf_spimWashType",
        validation_alias="xprs_cf_spimWashType"
    ) # FIXED CHOICE
    reagent: Optional[str] = Field(
        None,
        serialization_alias="xprs_cf_fk_reagent",
        validation_alias="xprs_cf_fk_reagent"
    ) # DYNAMIC CHOICE this might be a pk
    start_time: Optional[datetime] = Field(
        None,
        serialization_alias="xprs_cf_sbipDelipidationWash1Start",
        validation_alias="xprs_cf_sbipDelipidationWash1Start"
    )
    end_time: Optional[datetime] = Field(
        None,
        serialization_alias="xprs_cf_sbipDelipidationWash6End",
        validation_alias="xprs_cf_sbipDelipidationWash6End"
    )
    mass: Optional[Annotated[float | None, UnitSpec("&mu;g")]] = Field(
        None,
        serialization_alias="xprs_cf_mass",
        validation_alias="xprs_cf_mass"
    )
    notes: Optional[str] = Field(
        None,
        serialization_alias="xprs_cf_notes",
        validation_alias="xprs_cf_notes"
    )
    _base_fetch_filters: ClassVar[dict[str, Any]] = {
        "xprs_name": [
            "Wash 1",
            "Wash 2",
            "Wash 3",
            "Wash 4",
            "Refractive Index Matching Wash",
            "Primary Antibody Wash",
            "Secondary Antibody Wash",
            "MBS Wash",
            "Gelation PBS Wash",
            "Stock X + VA-044 Equilibration",
            "Gelation + ProK RT",
            "Gelation + Add'l ProK 37C",
            "Final PBS Wash"
        ]
    }