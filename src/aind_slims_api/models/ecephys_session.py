"""Contains a model for an ecephys result stored in SLIMS."""

from datetime import datetime
from typing import Annotated, ClassVar, List, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel
from aind_slims_api.models.utils import UnitSpec


class SlimsStreamsResult(SlimsBaseModel):
    """Model for a SLIMS Result Streams"""

    test_label: str = Field(
        "Streams", serialization_alias="test_label", validation_alias="test_label"
    )
    mouse_session: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession_display",
        validation_alias="rslt_cf_fk_mouseSession_display",
    )
    stream_modalities: Optional[List] = Field(
        default=None,
        serialization_alias="rslt_cf_streamModalities",
        validation_alias="rslt_cf_streamModalities",
    )
    daq_names: Optional[List] = Field(
        default=[],
        serialization_alias="rslt_cf_daqNames",
        validation_alias="rslt_cf_daqNames",
    )
    camera_names: Optional[List] = Field(
        default=None,
        serialization_alias="rslt_cf_cameraNames2",
        validation_alias="rslt_cf_cameraNames2",
    )
    # Look up in ReferenceDataRecord table
    stream_modules_pk: Optional[List] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_injectionMaterial2",
        validation_alias="rslt_cf_fk_injectionMaterial2",
    )
    pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_pk",
        validation_alias="rslt_pk",
    )
    mouse_pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_fk_content",
        validation_alias="rslt_fk_content",
    )
    mouse_session_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession",
        validation_alias="rslt_cf_fk_mouseSession",
    )
    experiment_run_step_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_fk_experimentRunStep",
        validation_alias="rslt_fk_experimentRunStep",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    _slims_table = "Result"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "test_name": "test_ephys_in_vivo_recording_stream",
    }


# TODO: Do we also need to check StimulusEpochs in ReferenceData?
class SlimsStimulusEpochsResult(SlimsBaseModel):
    """Model for a SLIMS Result Stimulus Epochs"""

    test_label: str = Field(
        "Stimulus Epochs",
        serialization_alias="test_label",
        validation_alias="test_label",
    )
    mouse_session: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession_display",
        validation_alias="rslt_cf_fk_mouseSession_display",
    )
    stimulus_device_names: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_stimulusDeviceNames",
        validation_alias="rslt_cf_stimulusDeviceNames",
    )
    stimulus_name: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_stimulusName",
        validation_alias="rslt_cf_stimulusName",
    )
    stimulus_modalities: Optional[List] = Field(
        default=None,
        serialization_alias="rslt_cf_stimulusModalities2",
        validation_alias="rslt_cf_stimulusModalities2",
    )
    reward_consumed_during_epoch: Annotated[float | None, UnitSpec("ml")] = Field(
        default=None,
        serialization_alias="rslt_cf_rewardConsumedDuringEpoch",
        validation_alias="rslt_cf_rewardConsumedDuringEpoch",
    )
    led_name: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_lightEmittingDiodeName",
        validation_alias="rslt_cf_lightEmittingDiodeName",
    )
    led_excitation_power_mw: Annotated[float | None, UnitSpec("mW")] = Field(
        default=None,
        serialization_alias="rslt_cf_lightEmittingDiodeExcitationPower",
        validation_alias="rslt_cf_lightEmittingDiodeExcitationPower",
    )
    laser_name: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_laserName",
        validation_alias="rslt_cf_laserName",
    )
    laser_wavelength: Annotated[float | None, UnitSpec("nm")] = Field(
        default=None,
        serialization_alias="rslt_laserWavelength",
        validation_alias="rslt_laserWavelength",
    )
    laser_excitation_power: Annotated[float | None, UnitSpec("mW")] = Field(
        default=None,
        serialization_alias="rslt_cf_laserExcitationPower",
        validation_alias="rslt_cf_laserExcitationPower",
    )
    speaker_name: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_speakerName",
        validation_alias="rslt_cf_speakerName",
    )
    speaker_volume: Annotated[float | None, UnitSpec("dB")] = Field(
        default=None,
        serialization_alias="rslt_cf_speakerVolume",
        validation_alias="rslt_cf_speakerVolume",
    )
    pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_pk",
        validation_alias="rslt_pk",
    )
    mouse_pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_fk_content",
        validation_alias="rslt_fk_content",
    )
    mouse_session_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession",
        validation_alias="rslt_cf_fk_mouseSession",
    )
    experiment_run_step_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_fk_experimentRunStep",
        validation_alias="rslt_fk_experimentRunStep",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    _slims_table = "Result"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "test_name": "test_stimulus_epochs",
    }


class SlimsMouseSessionResult(SlimsBaseModel):
    """Model for a SLIMS Result Mouse Session"""

    test_label: str = Field(
        "Mouse Session", serialization_alias="test_label", validation_alias="test_label"
    )
    mouse_session_id: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_uniqueIdentifier",
        validation_alias="rslt_uniqueIdentifier",
    )
    mouse_session: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession_display",
        validation_alias="rslt_cf_fk_mouseSession_display",
    )
    weight_prior_g: Annotated[float | None, UnitSpec("g")] = Field(
        default=None,
        serialization_alias="rslt_cf_animalWeightPrior",
        validation_alias="rslt_cf_animalWeightPrior",
    )
    weight_post_g: Annotated[float | None, UnitSpec("g")] = Field(
        default=None,
        serialization_alias="rslt_cf_animalWeightPost",
        validation_alias="rslt_cf_animalWeightPost",
    )
    reward_consumed_vol: Annotated[float | None, UnitSpec("ml")] = Field(
        default=None,
        serialization_alias="rslt_cf_rewardConsumedvolume",
        validation_alias="rslt_cf_rewardConsumedvolume",
    )
    reward_delivery_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_rewardDelivery",
        validation_alias="rslt_cf_fk_rewardDelivery",
    )
    pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_pk",
        validation_alias="rslt_pk",
    )
    mouse_pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_fk_content",
        validation_alias="rslt_fk_content",
    )
    mouse_session_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession",
        validation_alias="rslt_cf_fk_mouseSession",
    )
    experiment_run_step_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_fk_experimentRunStep",
        validation_alias="rslt_fk_experimentRunStep",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    _slims_table = "Result"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "test_name": "test_session_information",
    }


class SlimsEphysInsertionResult(SlimsBaseModel):
    """Model for a SLIMS Ephys Insertion Result"""

    test_label: str = Field(
        "EPHYS - Insertion",
        serialization_alias="test_label",
        validation_alias="test_label",
    )
    mouse_session: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession_display",
        validation_alias="rslt_cf_fk_mouseSession_display",
    )
    mouse_session_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_mouseSession",
        validation_alias="rslt_cf_fk_mouseSession",
    )
    dye: Optional[str] = Field(
        default=None, serialization_alias="rslt_cf_dye", validation_alias="rslt_cf_dye"
    )
    manipulator_x: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rslt_cf_manipulatorCoordinates",
        validation_alias="rslt_cf_manipulatorCoordinates",
    )
    manipulator_y: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rslt_cf_manipulatorY",
        validation_alias="rslt_cf_manipulatorY",
    )
    insertion_fail: Optional[bool] = Field(
        default=None,
        serialization_alias="rslt_cf_failed",
        validation_alias="rslt_cf_failed",
    )
    mouse_pk: Optional[int] = Field(
        None,
        serialization_alias="rslt_fk_content",
        validation_alias="rslt_fk_content",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    _slims_table = "Result"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "test_name": "test_ephys_insertion",
    }


class SlimsDomeModuleRdrc(SlimsBaseModel):
    """Model for Dome Module Reference Data"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="rdrc_pk", validation_alias="rdrc_pk"
    )
    implant_hole: Optional[float] = Field(
        default=None, serialization_alias="rdrc_cf_bsl", validation_alias="rdrc_cf_bsl"
    )
    assembly_name: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_assemblyName",
        validation_alias="rdrc_cf_assemblyName",
    )
    probe_name: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_probeName",
        validation_alias="rdrc_cf_probeName",
    )
    primary_targeted_structure_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rdrc_cf_fk_primaryTargetedStructure",
        validation_alias="rdrc_cf_fk_primaryTargetedStructure",
    )
    secondary_targeted_structures_pk: Optional[List] = Field(
        default=None,
        serialization_alias="rdrc_cf_fk_secondaryTargetedStructures",
        validation_alias="rdrc_cf_fk_secondaryTargetedStructures",
    )
    arc_angle: Annotated[float | None, UnitSpec("degree", "°")] = Field(
        default=None,
        serialization_alias="rdrc_cf_arcAngle",
        validation_alias="rdrc_cf_arcAngle",
    )
    module_angle: Annotated[float | None, UnitSpec("degree", "°")] = Field(
        default=None,
        serialization_alias="rdrc_cf_moduleAngle",
        validation_alias="rdrc_cf_moduleAngle",
    )
    rotation_angle: Annotated[float | None, UnitSpec("degree", "°")] = Field(
        default=None,
        serialization_alias="rdrc_cf_rotationAngle",
        validation_alias="rdrc_cf_rotationAngle",
    )
    coordinate_transform: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_manipulatorCalibrations_display",
        validation_alias="rdrc_cf_manipulatorCalibrations_display",
    )
    ccf_coordinate_ap: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_targetedCcfCoordinatesAp",
        validation_alias="rdrc_cf_targetedCcfCoordinatesAp",
    )
    ccf_coordinate_ml: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_targetedCcfCoordinatesMl",
        validation_alias="rdrc_cf_targetedCcfCoordinatesMl",
    )
    ccf_coordinate_dv: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_targetedCcfCoordinatesDv",
        validation_alias="rdrc_cf_targetedCcfCoordinatesDv",
    )
    ccf_version: Optional[float] = Field(
        default=None,
        serialization_alias="rdrc_cf_ccfVersion",
        validation_alias="rdrc_cf_ccfVersion",
    )
    bregma_target_ap: Annotated[
        float | None, UnitSpec("dm", "pm", "cm", "mm", "&mu;m", "nm", "m", "dam", "Tm")
    ] = Field(
        default=None,
        serialization_alias="rdrc_cf_targetAp",
        validation_alias="rdrc_cf_targetAp",
    )
    bregma_target_ml: Annotated[
        float | None, UnitSpec("dm", "pm", "cm", "mm", "&mu;m", "nm", "m", "dam", "Tm")
    ] = Field(
        default=None,
        serialization_alias="rdrc_cf_targetMl",
        validation_alias="rdrc_cf_targetMl",
    )
    bregma_target_dv: Annotated[
        float | None, UnitSpec("dm", "pm", "cm", "mm", "&mu;m", "nm", "m", "dam", "Tm")
    ] = Field(
        default=None,
        serialization_alias="rdrc_cf_targetDv",
        validation_alias="rdrc_cf_targetDv",
    )
    surface_z: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_surfaceZ",
        validation_alias="rdrc_cf_surfaceZ",
    )
    manipulator_x: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_manipulatorX",
        validation_alias="rdrc_cf_manipulatorX",
    )
    manipulator_y: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_manipulatory",
        validation_alias="rdrc_cf_manipulatory",
    )
    manipulator_z: Annotated[float | None, UnitSpec("&mu;m")] = Field(
        default=None,
        serialization_alias="rdrc_cf_manipulatorZ",
        validation_alias="rdrc_cf_manipulatorZ",
    )
    dye: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_fk_dye_display",
        validation_alias="rdrc_cf_fk_dye_display",
    )
    fiber_connections_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rdrc_cf_fk_fiberConnections",
        validation_alias="rdrc_cf_fk_fiberConnections",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "Dome Module",
    }


class SlimsBrainStructureRdrc(SlimsBaseModel):
    """Model for Brain Structure Reference Data"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="rdrc_pk", validation_alias="rdrc_pk"
    )
    name: Optional[str] = Field(
        default=None, serialization_alias="rdrc_name", validation_alias="rdrc_name"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "CCF brain structures",
    }


class SlimsFiberConnectionsRdrc(SlimsBaseModel):
    """Model for Fiber Connections Reference Data"""

    pk: Optional[int] = Field(serialization_alias="rdrc_pk", validation_alias="rdrc_pk")
    patch_cord_name: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_patchCordName",
        validation_alias="rdrc_cf_patchCordName",
    )
    patch_cord_output_power: Annotated[float | None, UnitSpec("&mu;W")] = Field(
        default=None,
        serialization_alias="rdrc_cf_patchCordOutputPower",
        validation_alias="rdrc_cf_patchCordOutputPower",
    )
    fiber_names: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_fiberNames",
        validation_alias="rdrc_cf_fiberNames",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "Fiber Connections",
    }


class SlimsRewardDeliveryRdrc(SlimsBaseModel):
    """Model for Reward Delivery Reference Data"""

    pk: Optional[int] = Field(serialization_alias="rdrc_pk", validation_alias="rdrc_pk")
    reward_spouts_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rdrc_cf_fk_rewardSpouts",
        validation_alias="rdrc_cf_fk_rewardSpouts",
    )
    # OPTIONS: "Water", or "Other (if Other, specify below)"
    reward_solution: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_rewardSolution",
        validation_alias="rdrc_cf_rewardSolution",
    )
    other_reward_solution: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_specifyrewardSolution",
        validation_alias="rdrc_cf_specifyrewardSolution",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "Reward Delivery",
    }


class SlimsRewardSpoutsRdrc(SlimsBaseModel):
    """Model for Reward Spouts Reference Data"""

    pk: Optional[int] = Field(serialization_alias="rdrc_pk", validation_alias="rdrc_pk")
    spout_side: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_spoutSide",
        validation_alias="rdrc_cf_spoutSide",
    )
    starting_position: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_startingPosition",
        validation_alias="rdrc_cf_startingPosition",
    )
    variable_position: Optional[bool] = Field(
        default=None,
        serialization_alias="rdrc_cf_variablePosition",
        validation_alias="rdrc_cf_variablePosition",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "Reward Spouts",
    }
