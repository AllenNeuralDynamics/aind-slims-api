import datetime
import logging
import os
from typing import Optional

from pydantic import BaseModel
from slims.slims import _SlimsApiException

import aind_slims_api
from .core import SlimsClient, PydanticFromSlims

logger = logging.getLogger()


class SLIMSWaterlogResult(PydanticFromSlims):
    rslt_cf_datePerformed: datetime.datetime
    rslt_cf_waterlogOperator: Optional[str]
    rslt_cf_weight: Optional[float]
    rslt_cf_waterEarned: Optional[float]
    rslt_cf_waterSupplementDelivered: Optional[float]
    rslt_cf_waterSupplementRecommended: Optional[float]
    rslt_cf_totalWater: Optional[float]
    rslt_comments: Optional[str]
    rslt_cf_fk_workStation: Optional[str]
    rslt_cf_swSource: str
    rslt_cf_swVersion: str
    rslt_pk: int


class SlimsWaterRestrictionEvent(PydanticFromSlims):
    cnvn_cf_startDate: datetime.datetime
    cnvn_cf_endDate: datetime.datetime
    cnvn_cf_assignedBy: str
    cnvn_cf_targetWeightFraction: float
    cntn_cf_contactPerson: str
    cntn_pk: int


class SLIMSMouseContent(PydanticFromSlims):
    cntn_cf_baselineWeight: Optional[float]
    cntn_cf_scientificPointOfContact: Optional[str]
    cntn_cf_waterRestricted: bool
    cntn_barCode: str
    cntn_pk: int

    # last_target_weight_fraction: Optional[float]
    # number_of_waterlog_records: Optional[int]
    # target_weight

    active_water_restriction_event: Optional[SlimsWaterRestrictionEvent] = None
    waterlog_records: list[SLIMSWaterlogResult] = []

    # TODO: Include other helpful fields (genotype, gender...)

    # pk: callable
    # cntn_fk_category: SlimsColumn
    # cntn_fk_contentType: SlimsColumn
    # cntn_barCode: SlimsColumn
    # cntn_id: SlimsColumn
    # cntn_cf_contactPerson: SlimsColumn
    # cntn_status: SlimsColumn
    # cntn_fk_status: SlimsColumn
    # cntn_fk_user: SlimsColumn
    # cntn_cf_fk_fundingCode: SlimsColumn
    # cntn_cf_genotype: SlimsColumn
    # cntn_cf_labtracksId: SlimsColumn
    # cntn_cf_parentBarcode: SlimsColumn


# https://aind-test.us.slims.agilent.com/slimsrest/rest/Content/2817
# https://aind-test.us.slims.agilent.com/slimsrest/rest/Result/1860
# https://aind-test.us.slims.agilent.com/slimsrest/rest/Test/66
# https://aind-test.us.slims.agilent.com/slimsrest/rest/ContentType/5


class WaterlogSlimsClient:

    def __init__(self, *args, **kwargs):
        self.client = SlimsClient(*args, **kwargs)

        self.get_useful_pks()

    def get_useful_pks(self):

        self.wl_test_pk = self.client.fetch_pk("Test", test_name="test_waterlog")

        self.mouse_contenttype_pk = self.client.fetch_pk("ContentType", cntp_name="Mouse")
        self.status_pending_pk = self.client.fetch_pk("Status", stts_name="Pending")

        self.wrest_event_pk = self.client.fetch_pk("ContentEventType", cnvt_uniqueIdentifier="cnvt_water_restriction")

        self.unit_pks = {
            "g": self.client.fetch("Unit", unit_name="gram")[0].pk(),
            "ml": self.client.fetch("Unit", unit_name="milliliter")[0].pk(),
        }

    def fetch_mouse_info(self, mouse_name: str) -> SLIMSMouseContent:
        """Fetches information and waterlog records for a mouse with labtracks id {mouse_name}"""
        mice = self.client.fetch(
            "Content",
            cntp_name="Mouse",
            cntn_barCode=mouse_name,
        )

        if len(mice) > 0:
            mouse_details = mice[0]
            if len(mice) > 1:
                logger.warning(
                    f"Warning, Multiple mice in SLIMS with barcode {mouse_name}, using pk={mouse_details.cntn_pk}"
                )
        else:
            logger.warning("Warning, Mouse not in SLIMS")

        # if mouse_details.cntn_cf_baselineWeight.unit != "g":
        #     raise NotImplementedError()

        # TODO: catch validation errors
        mouse = SLIMSMouseContent.from_slims_record(mouse_details)

        self.fetch_mouse_records(mouse)

        self.fetch_water_restriction_records(mouse)

        return mouse

    def fetch_mouse_records(self, mouse: SLIMSMouseContent) -> list[SLIMSWaterlogResult]:
        """Fetch "Waterlog" Results from SLIMS and update the mouse accordingly

        Args:
            mouse (MouseData): Mouse data object to be updated
            mouse_pk (int): SLIMS Primary Key for the mouse Content object

        Returns:
            list[WeightRecord]: Weight Record objects
        """

        slims_records = self.client.fetch(
            "Result",
            sort=["rslt_cf_datePerformed"],
            rslt_fk_content=mouse.cntn_pk,
            rslt_fk_test=self.wl_test_pk,
        )

        # TODO: catch validation errors
        records = [SLIMSWaterlogResult.from_slims_record(record) for record in slims_records]

        mouse.waterlog_records = records

    def fetch_water_restriction_records(self, mouse: SLIMSMouseContent) -> list[SlimsWaterRestrictionEvent]:
        """Fetch "Water Restriction" results from SLIMS and update the mouse accordingly

        Args:
            mouse (SLIMSMouseContent): Mouse data object to be updated

        Returns:
            list[SlimsWaterRestrictionEvent]: SLIMS records of water restriction events
        """

        slims_records: list[SlimsWaterRestrictionEvent] = self.client.fetch(
            "ContentEvent",
            sort=["cnvn_cf_startDate"],
            cnvn_fk_content=mouse.cntn_pk,
            cnvn_fk_contentEventType=self.wrest_event_pk,
        )

        # TODO: catch validation errors
        restriction_records = [SlimsWaterRestrictionEvent.from_slims_record(record) for record in slims_records]

        if len(restriction_records) > 0:
            latest_restriction = restriction_records[-1]
            event_active = latest_restriction.cnvn_cf_endDate is None
            if not (mouse.cntn_cf_waterRestricted == event_active):
                logger.warning(f"Warning, inconsistent water restricted data in SLIMS, MID, {mouse.cntn_barCode}")
            mouse.active_water_restriction_event = latest_restriction

    def add_waterlog_record(
        self,
        mouse: SLIMSMouseContent,
        record: SLIMSWaterlogResult,
        user: str,
        changed_baseline_weight: bool,
        changed_water_restricted: bool,
        changed_target_weight_fraction: bool,
        new_target_weight_fraction: Optional[float] = None,
    ):

        if changed_baseline_weight:
            self.post_baseline_weight(mouse)
        if changed_water_restricted:
            self.post_water_restricted(mouse, record.rslt_cf_datePerformed, user)
        if changed_target_weight_fraction:
            self.post_target_weight_fraction(mouse, record.rslt_cf_datePerformed, new_target_weight_fraction)

        self.client.add(
            "Result",
            {
                "rslt_fk_content": mouse.cntn_pk,
                "rslt_fk_test": self.wl_test_pk,
                "rslt_cf_datePerformed": int(record.rslt_cf_datePerformed.timestamp() * 10**3),
                "rslt_cf_waterlogOperator": user,
                "rslt_cf_weight": self.client.format_quantity(record.rslt_cf_weight, "g"),
                "rslt_cf_waterEarned": self.client.format_quantity(record.rslt_cf_waterEarned, "ml"),
                "rslt_cf_waterSupplementDelivered": self.client.format_quantity(
                    record.rslt_cf_waterSupplementDelivered, "ml"
                ),
                "rslt_cf_waterSupplementRecommended": self.client.format_quantity(
                    record.rslt_cf_waterSupplementRecommended, "ml"
                ),
                "rslt_comments": None if record.rslt_comments == "" else record.rslt_comments,
                "rslt_cf_fk_workStation": os.environ.get("aibs_comp_id", None),
                "rslt_cf_swSource": "WL",
                "rslt_cf_swVersion": aind_slims_api.__version__,
            },
        )

    def post_baseline_weight(self, mouse: SLIMSMouseContent):
        self.client.update(
            "Content",
            mouse.cntn_pk,
            {"cntn_cf_baselineWeight": self.client.format_quantity(mouse.cntn_cf_baselineWeight, "g")},
        )

    def post_water_restricted(self, mouse: SLIMSMouseContent, date: datetime.datetime, user: str, twf: float):

        self.client.update("Content", mouse.cntn_pk, {"cntn_cf_waterRestricted": mouse.cntn_cf_waterRestricted})

        if not mouse.cntn_cf_waterRestricted:
            if mouse.active_water_restriction_event is not None:
                self.client.update(
                    "ContentEvent",
                    mouse.active_water_restriction_event.cntn_pk,
                    {"cnvn_cf_endDate": int(date.timestamp() * 10**3)},
                )
        else:
            # Make new event
            self.client.add(
                "ContentEvent",
                {
                    "cnvn_fk_content": mouse.cntn_pk,
                    "cnvn_fk_contentEventType": self.wrest_event_pk,
                    "cnvn_cf_startDate": int(date.timestamp() * 10**3),
                    "cnvn_cf_targetWeightFraction": twf,
                    "cnvn_cf_assignedBy": user,
                },
            )

    def post_target_weight_fraction(self, mouse: SLIMSMouseContent, date: datetime.datetime, new_twf: float):
        self.client.update(
            "ContentEvent",
            mouse.active_water_restriction_event.cntn_pk,
            {"cnvn_cf_targetWeightFraction": new_twf},
        )

    def add_mouse(self, mouse: SLIMSMouseContent):  # TODO

        try:
            mouse = self.client.add(
                "Content",
                {
                    "cntn_fk_contentType": self.mouse_contenttype_pk,
                    "cntn_barCode": mouse.cntn_barCode,
                    "cntn_fk_status": self.status_pending_pk,
                },
            )
        except _SlimsApiException:
            logger.warning("Warning, could not add mouse to SLIMS")
            return mouse

        logger.info(f"SLIMS POST: Add Mouse {mouse.cntn_pk}, status code: 200")

        return mouse

    def get_links(self, mouse: SLIMSMouseContent):  # TODO: add to pydantic model?
        links = {
            "SLIMS Mouse Info": f"https://aind-test.us.slims.agilent.com/slimsrest/rest/Content/?cntn_cf_labtracksId={mouse.donor_name}",
            "SLIMS Mouse Results": f"https://aind-test.us.slims.agilent.com/slimsrest/rest/Result?rslt_fk_content={mouse.slims_pk}",
        }
        return links
