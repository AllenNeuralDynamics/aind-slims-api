"""Contains models for Imaging in SLIMS."""

from datetime import datetime
from typing import Annotated, Any, ClassVar, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel
from aind_slims_api.models.utils import UnitSpec

class SlimsImagingMetadata(SlimsBaseModel):
    """Model for a SLIMS Imaging Metadata"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="rslt_pk", validation_alias="rslt_pk"
    )
    date_performed: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_cf_datePerformed",
        validation_alias="rslt_cf_datePerformed",
    )
    sample_refractive_index: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_sampleRefractiveIndex1",
        validation_alias="rslt_cf_sampleRefractiveIndex1"
    )
    sample_immersion_medium: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_sampleImmersionMedium",
        validation_alias="rslt_cf_sampleImmersionMedium"
    )
    chamber_immersion_medium: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_cf_chamberImmersionMedium",
        validation_alias="rslt_cf_chamberImmersionMedium"
    )
    surgeon_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_surgeon",
        validation_alias="rslt_cf_fk_surgeon",
    )
    experiment_run_pk: Optional[int] = Field(
        default=None,
        serialization_alias="xprs_fk_experimentRun",
        validation_alias="xprs_fk_experimentRun",
    )
    brain_orientation_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_spimBrainOrientation ",
        validation_alias="rslt_cf_fk_spimBrainOrientation ",
    )
    instrument_json_pk: Optional[int] = Field(
        default=None,
        serialization_alias="rslt_cf_fk_instrumentJson",
        validation_alias="rslt_cf_fk_instrumentJson",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_createdOn",
        validation_alias="rslt_createdOn",
    )
    created_by: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_createdBy",
        validation_alias="rslt_createdBy",
    )
    modified_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rslt_modifiedOn",
        validation_alias="rslt_modifiedOn",
    )
    modified_by: Optional[str] = Field(
        default=None,
        serialization_alias="rslt_modifiedBy",
        validation_alias="rslt_modifiedBy",
    )
    _slims_table = "Result"
