"""Contains a model for a waterlog result stored in SLIMS."""

from datetime import datetime
from typing import Annotated, ClassVar, Optional

from pydantic import Field

from aind_slims_api import __version__
from aind_slims_api.models.base import SlimsBaseModel
from aind_slims_api.models.utils import UnitSpec


class SlimsWaterlogResult(SlimsBaseModel):
    """Model for a SLIMS Waterlog Result, the daily water/weight records

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> from aind_slims_api import models
    >>> client = SlimsClient()
    >>> mouse_pk = client.fetch_pk("Content", cntn_barCode="00000000",
    ...  cntp_name="Mouse"
    ... )
    >>> test_pk = client.fetch_pk("Test", test_name="test_waterlog")

    Write waterlog result.
    >>> waterlog_result = client.add_model(
    ...  models.SlimsWaterlogResult(
    ...   date=datetime(2021,1,1),
    ...   weight_g=20.0,
    ...   water_earned_ml=5.0,
    ...   water_supplement_delivered_ml=5.0,
    ...   water_supplement_recommended_ml=5.0,
    ...   total_water_ml=10.0,
    ...   comments="comments",
    ...   workstation="aibs-computer-id",
    ...  ),
    ...  overloads={
    ...   "rslt_fk_content": mouse_pk,
    ...   "rslt_fk_test": test_pk,
    ...  }
    ... )

    Read waterlog results.
    >>> waterlog_result = client.fetch_model(
    ...  models.SlimsWaterlogResult,
    ...  rslt_fk_content=mouse_pk,
    ...  rslt_fk_test=test_pk,
    ... )
    >>> waterlog_result.weight_g
    20.0
    """
    date: datetime = Field(
        datetime.now(),
        serialization_alias="rslt_cf_datePerformed",
        validation_alias="rslt_cf_datePerformed",
    )
    operator: Optional[str] = Field(
        None,
        serialization_alias="rslt_cf_waterlogOperator",
        validation_alias="rslt_cf_waterlogOperator",
    )
    weight_g: Annotated[float | None, UnitSpec("g")] = Field(
        None,
        serialization_alias="rslt_cf_weight",
        validation_alias="rslt_cf_weight",
    )
    water_earned_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ...,
        serialization_alias="rslt_cf_waterEarned",
        validation_alias="rslt_cf_waterEarned",
    )
    water_supplement_delivered_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ...,
        serialization_alias="rslt_cf_waterSupplementDelivered",
        validation_alias="rslt_cf_waterSupplementDelivered",
    )
    water_supplement_recommended_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ...,
        serialization_alias="rslt_cf_waterSupplementRecommended",
        validation_alias="rslt_cf_waterSupplementRecommended",
    )
    total_water_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ...,
        serialization_alias="rslt_cf_totalWater",
        validation_alias="rslt_cf_totalWater",
    )
    comments: Optional[str] = Field(
        None,
        serialization_alias="rslt_comments",
        validation_alias="rslt_comments",
    )
    workstation: Optional[str] = Field(
        None,
        serialization_alias="rslt_cf_fk_workStation",
        validation_alias="rslt_cf_fk_workStation",
    )
    sw_source: str = Field(
        "aind-slims-api",
        serialization_alias="rslt_cf_swSource",
        validation_alias="rslt_cf_swSource",
    )
    sw_version: str = Field(
        __version__,
        serialization_alias="rslt_cf_swVersion",
        validation_alias="rslt_cf_swVersion",
    )

    _slims_table = "Result"
