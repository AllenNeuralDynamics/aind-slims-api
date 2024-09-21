"""Contains a model for an ecephys result stored in SLIMS."""

from datetime import datetime
from typing import Annotated, List, Optional, ClassVar
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
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    _slims_table = "Result"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "test_name": "test_ephys_in_vivo_recording_stream",
    }


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
        serialization_alias="rslt_cf_stimulusDeviceNames",
        validation_alias="rslt_cf_stimulusDeviceNames",
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
    mouse_session_id: str = Field(
        ...,
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
    reward_delivery: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_rewardDelivery",
        validation_alias="rslt_cf_rewardDelivery",
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
    manipulator_x: Annotated[float | None, UnitSpec("um")] = Field(
        default=None,
        serialization_alias="rslt_cf_manipulatorCoordinates",
        validation_alias="rslt_cf_manipulatorCoordinates",
    )
    manipulator_y: Annotated[float | None, UnitSpec("um")] = Field(
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
