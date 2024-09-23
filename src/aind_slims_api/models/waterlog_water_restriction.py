"""Contains a model for a waterlog water restriction event stored in SLIMS."""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel

DEFAULT_WEIGHT_FRACTION = 0.85
MIN_WEIGHT_FRACTION = 0.75
MAX_WEIGHT_FRACTION = 1.0


class SlimsWaterRestrictionEvent(SlimsBaseModel):
    """Model for a Water Restriction Event

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> from aind_slims_api import models
    >>> client = SlimsClient()
    >>> mouse = client.fetch_model(models.SlimsMouseContent, barcode="00000000")

    ### Write
    >>> water_restriction_event = client.add_model(
    ...  models.SlimsWaterRestrictionEvent(
    ...   mouse_pk=mouse.pk,
    ...   start_date=datetime(2021,1,1),
    ...   end_date=datetime(2021,1,2),
    ...   assigned_by="mochic",
    ...   target_weight_fraction=0.90,
    ...  )
    ... )

    ### Read
    >>> water_restriction_event = client.fetch_model(
    ...  models.SlimsWaterRestrictionEvent,
    ...  mouse_pk=mouse.pk,
    ... )
    >>> water_restriction_event.target_weight_fraction
    0.9
    """

    start_date: datetime = Field(
        datetime.now(),
        serialization_alias="cnvn_cf_startDate",
        validation_alias="cnvn_cf_startDate",
    )
    end_date: Optional[datetime] = Field(
        None,
        serialization_alias="cnvn_cf_endDate",
        validation_alias="cnvn_cf_endDate",
    )
    assigned_by: str = Field(
        ...,
        serialization_alias="cnvn_cf_assignedBy",
        validation_alias="cnvn_cf_assignedBy",
    )
    target_weight_fraction: float = Field(
        default=DEFAULT_WEIGHT_FRACTION,
        serialization_alias="cnvn_cf_targetWeightFraction",
        validation_alias="cnvn_cf_targetWeightFraction",
        gt=MIN_WEIGHT_FRACTION,
        lt=MAX_WEIGHT_FRACTION,
    )
    pk: Optional[int] = Field(
        None,
        serialization_alias="cnvn_pk",
        validation_alias="cnvn_pk",
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="cnvn_createdOn",
        validation_alias="cnvn_createdOn",
    )
    mouse_pk: Optional[int] = Field(
        None,
        serialization_alias="cnvn_fk_content",
        validation_alias="cnvn_fk_content",
    )
    cnvn_fk_contentEventType: int = 9  # pk of Water Restriction ContentEvent type

    _slims_table = "ContentEvent"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "cnvt_name": "Water Restriction",
    }
