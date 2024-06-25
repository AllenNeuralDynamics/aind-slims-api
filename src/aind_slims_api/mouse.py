"""Contains a model for the mouse content, and a method for fetching it"""

import logging
from typing import Annotated

from pydantic import Field, BeforeValidator, ValidationError

from aind_slims_api.core import SlimsBaseModel, SlimsClient, UnitSpec, SLIMSTABLES

logger = logging.getLogger()


class SlimsMouseContent(SlimsBaseModel):
    """Model for an instance of the Mouse ContentType"""

    baseline_weight_g: Annotated[float | None, UnitSpec("g")] = Field(
        ..., alias="cntn_cf_baselineWeight"
    )
    point_of_contact: str | None = Field(..., alias="cntn_cf_scientificPointOfContact")
    water_restricted: Annotated[bool, BeforeValidator(lambda x: x or False)] = Field(
        ..., alias="cntn_cf_waterRestricted"
    )
    barcode: str = Field(..., alias="cntn_barCode")
    pk: int = Field(..., alias="cntn_pk")

    _slims_table: SLIMSTABLES = "Content"

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


def fetch_mouse_content(
    client: SlimsClient,
    mouse_name: str,
) -> SlimsMouseContent | dict | None:
    """Fetches mouse information for a mouse with labtracks id {mouse_name}"""
    mice = client.fetch(
        "Content",
        cntp_name="Mouse",
        cntn_barCode=mouse_name,
    )

    if len(mice) > 0:
        mouse_details = mice[0]
        if len(mice) > 1:
            logger.warning(
                f"Warning, Multiple mice in SLIMS with barcode "
                f"{mouse_name}, using pk={mouse_details.cntn_pk.value}"
            )
    else:
        logger.warning("Warning, Mouse not in SLIMS")
        return

    try:
        mouse = SlimsMouseContent.model_validate(mouse_details)
    except ValidationError as e:
        logger.error(f"SLIMS data validation failed, {repr(e)}")
        return mouse_details.json_entity

    return mouse
