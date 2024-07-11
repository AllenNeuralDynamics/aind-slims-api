"""Contains models for Waterlog Results and Water Restriction Events and
methods for fetching each of those.

Also contains a Mouse class for keeping track of relevant data for a given
mouse and fetching/updating/posting data to SLIMS"""

from datetime import datetime
import logging
import os
from typing import Annotated, Optional

from pydantic import Field, ValidationError

import aind_slims_api
from aind_slims_api.user import SlimsUser
from aind_slims_api.core import SLIMSTABLES, SlimsClient, SlimsBaseModel, UnitSpec
from aind_slims_api.mouse import SlimsMouseContent, fetch_mouse_content
from aind_slims_api import config

logger = logging.getLogger()


class SLIMSWaterlogResult(SlimsBaseModel):
    """Model for a SLIMS Waterlog Result, the daily water/weight records"""

    date: datetime = Field(datetime.now(), alias="rslt_cf_datePerformed")
    operator: Optional[str] = Field(None, alias="rslt_cf_waterlogOperator")
    weight_g: Annotated[float | None, UnitSpec("g")] = Field(
        None, alias="rslt_cf_weight"
    )
    water_earned_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ..., alias="rslt_cf_waterEarned"
    )
    water_supplement_delivered_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ..., alias="rslt_cf_waterSupplementDelivered"
    )
    water_supplement_recommended_ml: Annotated[float | None, UnitSpec("ml")] = Field(
        ..., alias="rslt_cf_waterSupplementRecommended"
    )
    total_water: Annotated[float | None, UnitSpec("ml")] = Field(
        ..., alias="rslt_cf_totalWater"
    )
    comments: Optional[str] = Field(None, alias="rslt_comments")
    work_station: Optional[str] = Field(None, alias="rslt_cf_fk_workStation")
    sw_source: str = Field("aind-slims-api", alias="rslt_cf_swSource")
    sw_version: str = Field(aind_slims_api.__version__, alias="rslt_cf_swVersion")
    pk: Optional[int] = Field(None, alias="rslt_pk")
    fk_content: Optional[int] = Field(None, alias="rslt_fk_content")
    fk_test: Optional[int] = Field(None, alias="rslt_fk_test")

    _slims_table: SLIMSTABLES = "Result"


class SlimsWaterRestrictionEvent(SlimsBaseModel):
    """Model for a Water Restriction Event"""

    start_date: datetime = Field(datetime.now(), alias="cnvn_cf_startDate")
    end_date: Optional[datetime] = Field(None, alias="cnvn_cf_endDate")
    assigned_by: str = Field(..., alias="cnvn_cf_assignedBy")
    target_weight_fraction: float = Field(
        default=config.wl_default_target_weight_fraction,
        alias="cnvn_cf_targetWeightFraction",
        gt=config.wl_min_target_weight_fraction,
        lt=config.wl_max_target_weight_fraction,
    )
    pk: int = Field(None, alias="cnvn_pk")
    fk_content: int = Field(None, alias="cnvn_fk_content")
    fk_contentEventType: int = Field(None, alias="cnvn_fk_contentEventType")

    _slims_table: SLIMSTABLES = "ContentEvent"


def fetch_mouse_waterlog_results(
    client: SlimsClient,
    mouse: SlimsMouseContent,
) -> list[SLIMSWaterlogResult]:
    """Fetch "Waterlog" Results from SLIMS

    Args:
        client (SlimsClient): SLIMS client object
        mouse (SlimsMouseContent): Mouse data object

    Returns:
        list[SLIMSWaterlogResult]: Waterlog record objects
    """

    slims_records = client.fetch(
        "Result",
        sort=["rslt_cf_datePerformed"],
        rslt_fk_content=mouse.pk,
        test_name="test_waterlog",
    )

    try:
        records = [
            SLIMSWaterlogResult.model_validate(record) for record in slims_records
        ]
    except ValidationError as e:
        logger.error(f"SLIMS data validation failed, {repr(e)}")
        return [r.json_entity for r in slims_records]

    return records


def fetch_water_restriction_events(
    client: SlimsClient,
    mouse: SlimsMouseContent,
) -> list[SlimsWaterRestrictionEvent]:
    """Fetch all historical "Water Restriction" events from SLIMS

    Args:
        client (SlimsClient): SLIMS client object
        mouse (SlimsMouseContent): Mouse data object

    Returns:
        list[SlimsWaterRestrictionEvent]: SLIMS records of events
    """

    slims_records: list[SlimsWaterRestrictionEvent] = client.fetch(
        "ContentEvent",
        sort=["cnvn_cf_startDate"],
        cnvn_fk_content=mouse.pk,
        cnvt_name="Water Restriction",
    )

    try:
        restriction_records = [
            SlimsWaterRestrictionEvent.model_validate(record)
            for record in slims_records
        ]
    except ValidationError as e:
        logger.error(f"SLIMS data validation failed, {repr(e)}")
        return [r.json_entity for r in slims_records]

    return restriction_records


class Mouse:
    """Class for tracking mouse water/weight data and syncing with SLIMS"""

    def __init__(self, mouse_name: str, user: SlimsUser, slims_client=None):
        """Fetch data from Slims for mouse with barcode={mouse_name}"""
        self.client = slims_client or SlimsClient()
        self.mouse_name = mouse_name
        self.user = user

        self.mouse: SlimsMouseContent = None
        self.waterlog_results: list[SLIMSWaterlogResult] = []
        self.restriction: SlimsWaterRestrictionEvent = None
        self.all_restrictions: list[SlimsWaterRestrictionEvent] = []

        self.link_mouse: str = None
        self.link_restrictions: str = None
        self.link_wl_records: str = None

        self._fetch_data()
        self._fetch_pks()

    def _fetch_data(self):
        """Fetches mouse/waterlog/restriction data from SLIMS"""

        self.mouse = fetch_mouse_content(self.client, self.mouse_name)
        self.waterlog_results = fetch_mouse_waterlog_results(self.client, self.mouse)
        self.all_restrictions = fetch_water_restriction_events(self.client, self.mouse)

        if len(self.all_restrictions) > 0:
            latest_restriction = self.all_restrictions[-1]
            event_active = latest_restriction.end_date is None
            if not (self.mouse.water_restricted == event_active):
                logger.warning(
                    f"Warning, inconsistent water restricted data in SLIMS, "
                    f"MID, {self.mouse.barcode}"
                )
            self.restriction = latest_restriction if event_active else None

        self._make_links()

    def _make_links(self):
        """Constructs useful links to SLIMS tables"""
        self.link_mouse = self.client.rest_link(
            "Content", cntn_cf_labtracksId=self.mouse_name
        )
        self.link_wl_records = self.client.rest_link(
            "Result", rslt_fk_content=self.mouse_name
        )
        self.link_restrictions = self.client.rest_link(
            "ContentEvent", cnvn_fk_content=self.mouse_name
        )

    def _fetch_pks(self):
        """Fetches useful SLIMS pks"""
        self.wrest_pk = self.client.fetch_pk(
            "ContentEventType", cnvt_uniqueIdentifier="cnvt_water_restriction"
        )
        self.wl_test_pk = self.client.fetch_pk("Test", test_name="test_waterlog")

    def add_waterlog_record(
        self,
        weight: float,
        water_earned: float,
        water_supplement_recommended: float,
        water_supplement_delivered: float,
        total_water: float = None,
        comments: str = None,
    ):
        """Creates and adds a new waterlog weight/water record to SLIMS, and
        updates self.waterlog_results accordingly"""
        if total_water is None:
            total_water = water_earned + water_supplement_delivered

        record = SLIMSWaterlogResult(
            rslt_cf_weight=weight,
            rslt_cf_waterEarned=water_earned,
            rslt_cf_waterSupplementDelivered=water_supplement_recommended,
            rslt_cf_waterSupplementRecommended=water_supplement_delivered,
            rslt_cf_totalWater=total_water,
            rslt_comments=comments,
            rslt_fk_test=self.wl_test_pk,
            rslt_fk_content=self.mouse.pk,
            rslt_cf_fk_workStation=os.environ.get("aibs_comp_id", None),
        )

        record = self.client.add_model(record)
        self.waterlog_results.append(record)
        logger.info("Added SLIMS Waterlog record")

    def post_baseline_weight(self, new_baseline_weight: float):
        """Update the baseline weight in SLIMS and self.mouse"""
        self.mouse.baseline_weight_g = new_baseline_weight
        self.mouse = self.client.update_model(self.mouse, "baseline_weight")
        logger.info(
            f"Updated mouse {self.mouse_name} "
            f"baseline weight to {new_baseline_weight}"
        )

    def switch_to_water_restricted(self, target_weight_fraction: float):
        """If the mouse is on ad-lib water,
        - Create a water restriction event starting today
        - Update the mouse's water_restricted field
        - Update SLIMS with the above
        - Update local data accordingly"""
        if self.mouse.water_restricted:
            logger.info("Mouse is already water restricted")
            return

        new_restriction = SlimsWaterRestrictionEvent(
            cnvn_cf_assignedBy=self.user.full_name,
            cnvn_cf_targetWeightFraction=target_weight_fraction,
            cnvn_fk_content=self.mouse.pk,
            cnvn_fk_contentEventType=self.wrest_pk,
        )
        self.mouse.water_restricted = True
        self.mouse = self.client.update_model(self.mouse, "water_restricted")

        self.restriction = self.client.add_model(new_restriction)
        self.all_restrictions.append(self.restriction)
        logger.info(f"Switched mouse {self.mouse_name} to Water Restricted")

    def switch_to_adlib_water(self):
        """If the mouse is water restricted,
        - Set the end date of the active restriction event to today
        - Update the mouse's water_restricted field
        - Update SLIMS with the above
        - Update local data accordingly"""
        if not self.mouse.water_restricted:
            logger.info("Mouse is already on ad-lib water")
            return

        self.mouse.water_restricted = False
        self.mouse = self.client.update_model(self.mouse, "water_restricted")

        self.restriction.end_date = datetime.now()
        self.restriction = self.client.update_model(self.restriction, "end_date")
        self.restriction = None
        logger.info(f"Switched mouse {self.mouse_name} to Adlib Water")

    def update_target_weight_fraction(self, new_twf: float):
        """Update the target weight fraction of the active restriction"""
        if not self.mouse.water_restricted:
            logger.info("Mouse is not water restricted")
            return
        self.restriction.target_weight_fraction = new_twf
        self.restriction = self.client.update_model(
            self.restriction, "target_weight_fraction"
        )
        logger.info(
            f"Updated mouse {self.mouse_name} " f"target weight fraction to {new_twf}"
        )
