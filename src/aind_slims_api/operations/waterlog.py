"""Common operations for logging mouse water and weight with the SLIMS API."""

from datetime import datetime
from typing import Optional
import os
import logging

from pydantic import BaseModel, model_validator, validate_call

from aind_slims_api import models, SlimsClient, exceptions
from aind_slims_api.models import (
    SlimsMouseContent,
    SlimsWaterlogResult,
    SlimsWaterRestrictionEvent,
    SlimsUser,
)
from aind_slims_api.models.base import SlimsBaseModel

logger = logging.getLogger(__name__)


class WaterlogMouseOperator:
    """Class for tracking mouse water/weight data and syncing with SLIMS

    Examples
    --------

    >>> from aind_slims_api import SlimsClient

    >>> client = SlimsClient()
    >>> user = client.fetch_model(SlimsUser,username='username')
    >>> barcode = '000000'

    >>> mouse = Mouse(barcode,user,client)

    >>> print(f'Mouse {barcode} baseline weight is {mouse.details.baseline_weight_g} g')

    >>> if mouse.details.water_restricted:
    ...     mouse.switch_to_adlib_water()

    >>> mouse.add_waterlog_record(
    ...     weight=20,
    ...     water_earned=0,
    ...     water_supplement_recommended=1,
    ...     water_supplement_delivered=1,
    ... )

    >>> mouse.post_baseline_weight(20)

    >>> mouse.switch_to_water_restricted()

    >>> mouse.update_target_weight_fraction(0.9)

    """

    client: SlimsClient
    user: SlimsUser
    barcode: str

    details: SlimsMouseContent
    waterlog_results: list[SlimsWaterlogResult]
    restriction: SlimsWaterRestrictionEvent | None
    all_restrictions: list[SlimsWaterRestrictionEvent]

    def __init__(self, barcode: str, user: SlimsUser, slims_client=None):
        """Fetch data from Slims for mouse with barcode={mouse_name}"""
        self.client = slims_client or SlimsClient()
        self.barcode = barcode
        self.user = user

        self.details: SlimsMouseContent = None
        self.waterlog_results: list[SlimsWaterlogResult] = []
        self.restriction: SlimsWaterRestrictionEvent = None
        self.all_restrictions: list[SlimsWaterRestrictionEvent] = []

        self.link_mouse: str = None
        self.link_restrictions: str = None
        self.link_wl_records: str = None

        self._fetch_data()
        self._fetch_pks()

    def _fetch_data(self):
        """Fetches mouse/waterlog/restriction data from SLIMS"""

        self.details = self.client.fetch_model(
            SlimsMouseContent,
            barcode=self.barcode,
        )
        self.waterlog_results = self.client.fetch_models(
            SlimsWaterlogResult,
            mouse_pk=self.details.pk,
        )
        self.all_restrictions = self.client.fetch_models(
            SlimsWaterRestrictionEvent,
            mouse_pk=self.details.pk,
        )

        if len(self.all_restrictions) > 0:
            latest_restriction = self.all_restrictions[-1]
            event_active = latest_restriction.end_date is None
            if not (self.details.water_restricted == event_active):
                logger.warning(f"Warning, inconsistent water restricted data in SLIMS, " f"MID, {self.details.barcode}")
            self.restriction = latest_restriction if event_active else None

        self._make_links()

    def _make_links(self):
        """Constructs useful links to SLIMS tables"""
        self.link_mouse = self.client.rest_link(SlimsMouseContent._slims_table, cntn_cf_labtracksId=self.barcode)
        self.link_wl_records = self.client.rest_link(SlimsWaterlogResult._slims_table, rslt_fk_content=self.barcode)
        self.link_restrictions = self.client.rest_link(
            SlimsWaterRestrictionEvent._slims_table, cnvn_fk_content=self.barcode
        )

    def _fetch_pks(self):
        """Fetches useful SLIMS pks"""
        self.wrest_pk = self.client.fetch_pk("ContentEventType", cnvt_uniqueIdentifier="cnvt_water_restriction")
        self.wl_test_pk = self.client.fetch_pk("Test", test_name="test_waterlog")

    def add_waterlog_record(
        self,
        weight: float,
        water_earned: float,
        water_supplement_recommended: float,
        water_supplement_delivered: float,
        comments: Optional[str] = None,
        workstation: Optional[str] = None,
    ):
        """Creates and adds a new waterlog weight/water record to SLIMS, and
        updates self.waterlog_results accordingly"""

        total_water = water_earned + water_supplement_delivered

        record = SlimsWaterlogResult(
            weight_g=weight,
            water_earned_ml=water_earned,
            water_supplement_recommended_ml=water_supplement_recommended,
            water_supplement_delivered_ml=water_supplement_delivered,
            total_water_ml=total_water,
            comments=comments,
            test_pk=self.wl_test_pk,
            mouse_pk=self.details.pk,
            workstation=workstation or os.environ.get("aibs_comp_id", None),
        )

        record = self.client.add_model(record)
        self.waterlog_results.append(record)
        logger.info("Added SLIMS Waterlog record")

    def post_baseline_weight(self, new_baseline_weight: float):
        """Update the baseline weight in SLIMS and self.details"""
        self.details.baseline_weight_g = new_baseline_weight
        self.details = self.client.update_model(self.details, "baseline_weight_g")
        logger.info(f"Updated mouse {self.barcode} " f"baseline weight to {new_baseline_weight}")

    def switch_to_water_restricted(self, target_weight_fraction: float):
        """If the mouse is on ad-lib water,
        - Create a water restriction event starting today
        - Update the mouse's water_restricted field
        - Update SLIMS with the above
        - Update local data accordingly"""
        if self.details.water_restricted:
            logger.info("Mouse is already water restricted")
            return

        new_restriction = SlimsWaterRestrictionEvent(
            assigned_by=self.user.full_name,
            target_weight_fraction=target_weight_fraction,
            mouse_pk=self.details.pk,
            cnvn_fk_contentEventType=self.wrest_pk,
        )
        self.details.water_restricted = True
        self.details = self.client.update_model(self.details, "water_restricted")

        self.restriction = self.client.add_model(new_restriction)
        self.all_restrictions.append(self.restriction)
        logger.info(f"Switched mouse {self.barcode} to Water Restricted")

    def switch_to_adlib_water(self):
        """If the mouse is water restricted,
        - Set the end date of the active restriction event to today
        - Update the mouse's water_restricted field
        - Update SLIMS with the above
        - Update local data accordingly"""
        if not self.details.water_restricted:
            logger.info("Mouse is already on ad-lib water")
            return

        self.details.water_restricted = False
        self.details = self.client.update_model(self.details, "water_restricted")

        self.restriction.end_date = datetime.now()
        self.restriction = self.client.update_model(self.restriction, "end_date")
        self.restriction = None
        logger.info(f"Switched mouse {self.barcode} to Adlib Water")

    def update_target_weight_fraction(self, new_twf: float):
        """Update the target weight fraction of the active restriction"""
        if not self.details.water_restricted:
            logger.info("Mouse is not water restricted")
            return
        self.restriction.target_weight_fraction = new_twf
        self.restriction = self.client.update_model(self.restriction, "target_weight_fraction")
        logger.info(f"Updated mouse {self.barcode} " f"target weight fraction to {new_twf}")
