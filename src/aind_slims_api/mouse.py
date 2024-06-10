"""Contains a model for the mouse content, and a method for fetching it"""

import logging

from .core import SlimsClient

logger = logging.getLogger()


def fetch_mouse_content(
    client: SlimsClient,
    mouse_name: str,
) -> dict:
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
                f"{mouse_name}, using pk={mouse_details.cntn_pk}"
            )
    else:
        logger.warning("Warning, Mouse not in SLIMS")
        return

    return mouse_details
