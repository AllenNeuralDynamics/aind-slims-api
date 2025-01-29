"""Contains models for Imaging in SLIMS."""

from datetime import datetime
from typing import ClassVar, Optional
from pydantic import Field
from aind_slims_api.models.base import SlimsBaseModel


class SlimsImagingMetadataResult(SlimsBaseModel):
    """Model for a SLIMS Imaging Metadata"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="rslt_pk", validation_alias="rslt_pk"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    modified_by: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_modifiedBy",
        validation_alias="rslt_modifiedBy",
    )
    content_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_fk_content",
        validation_alias="rslt_fk_content",
    )
    date_performed: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_cf_datePerformed",
        validation_alias="rslt_cf_datePerformed",
    )
    sample_refractive_index: Optional[float] = Field(
        default=None,
        serialization_alias="rslt_cf_sampleRefractiveIndex1",
        validation_alias="rslt_cf_sampleRefractiveIndex1",
    )
    sample_immersion_medium: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_sampleImmersionMedium",
        validation_alias="rslt_cf_sampleImmersionMedium",
    )
    chamber_refractive_index: Optional[float] = Field(
        default=None,
        serialization_alias="rslt_cf_chamberRefractiveIndex",
        validation_alias="rslt_cf_chamberRefractiveIndex",
    )
    chamber_immersion_medium: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_chamberImmersionMedium",
        validation_alias="rslt_cf_chamberImmersionMedium",
    )
    notes: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_comments",
        validation_alias="rslt_comments",
    )
    experiment_run_step_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_fk_experimentRunStep",
        validation_alias="rslt_fk_experimentRunStep",
    )
    surgeon_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_surgeon",
        validation_alias="rslt_cf_fk_surgeon",
    )
    brain_orientation_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_spimBrainOrientation",
        validation_alias="rslt_cf_fk_spimBrainOrientation",
    )
    instrument_json_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_instrumentJson",
        validation_alias="rslt_cf_fk_instrumentJson",
    )
    _slims_table = "Result"


class SlimsSPIMBrainOrientationRdrc(SlimsBaseModel):
    """Model for a SLIMS Brain Orientation"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="rdrc_pk", validation_alias="rdrc_pk"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    modified_by: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_modifiedBy",
        validation_alias="rdrc_modifiedBy",
    )
    name: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_name",
        validation_alias="rdrc_name",
    )
    z_direction: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_washType",
        validation_alias="rdrc_cf_washType",
    )
    y_direction: Optional[str] = Field(
        default=None,
        validation_alias="rdrc_cf_additionalWashReagent",
        serialization_alias="rdrc_cf_additionalWashReagent",
    )
    x_direction: Optional[str] = Field(
        default=None,
        serialization_alias="rdrc_cf_hostSpecies",
        validation_alias="rdrc_cf_hostSpecies",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "SPIM Brain Orientation",
    }
