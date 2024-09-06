"""Common operations for the SLIMS API.
"""

from datetime import datetime
from typing import Optional

from aind_slims_api import models, SlimsClient, exceptions


def get_waterlog_suggestion(
    client: SlimsClient,
    mouse: str | models.SlimsMouseContent,
    current_weight: float,
    water_restriction_event: Optional[models.SlimsWaterRestrictionEvent] = None,
) -> float:
    """Helper function for getting the waterlog water suggestion in ml for a
     mouse. If mouse has no baseline weight returns None.

    Raises
    ------
    exceptions.SlimsApiException
        If the mouse has no baseline weight.

    Examples
    --------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    >>> suggestion = get_waterlog_suggestion(client, "123456", 30.0)
    """
    if isinstance(mouse, str):
        mouse = client.fetch_model(
            models.SlimsMouseContent, barcode=mouse)

    if water_restriction_event is None:
        water_restriction_event = client.fetch_model(
            models.SlimsWaterRestrictionEvent,
            mouse_pk=mouse.pk,
        )

    if mouse.baseline_weight_g is None:
        raise exceptions.SlimsAPIException(
            "Mouse has no baseline weight, cannot calculate water suggestion."
        )

    return (water_restriction_event.target_weight_fraction * mouse.baseline_weight_g) \
        - current_weight


def write_waterlog_result(
    client: SlimsClient,
    mouse: str | models.SlimsMouseContent,
    date: datetime,
    weight_g: float,
    water_earned_ml: float,
    water_supplement_delivered_ml: float,
    comments: Optional[str] = None,
    workstation_name: Optional[str] = None,
    water_supplement_recommended_ml: Optional[float] = None,
) -> models.SlimsWaterlogResult:
    """Helper function for writing a waterlog result.

    Examples
    --------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    >>> result_record = write_waterlog_result(
    ...  client,
    ...  "00000000",
    ...  datetime.now(),
    ...  30.0,
    ...  5.0,
    ...  5.0,
    ...  "comments",
    ...  "aibs-computer-id",
    ... )
    """
    if isinstance(mouse, str):
        mouse = client.fetch_model(
            models.SlimsMouseContent, barcode=mouse)
    
    test_pk = client.fetch_pk("Test", test_name="test_waterlog")  # TODO: Explain why SLIMS needs this

    return client.add_model(
        models.SlimsWaterlogResult(
            mouse_pk=mouse.pk,
            date=date,
            weight_g=weight_g,
            water_earned_ml=water_earned_ml,
            water_supplement_delivered_ml=water_supplement_delivered_ml,
            water_supplement_recommended_ml=water_supplement_recommended_ml,
            total_water_ml=water_earned_ml + water_supplement_delivered_ml,
            comments=comments,
            workstation=workstation_name,
            test_pk=test_pk,
        )
    )
