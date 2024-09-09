"""Common operations for logging mouse water and weight with the SLIMS API.

Examples
--------
>>> import datetime
>>> from aind_slims_api import SlimsClient
>>> from aind_slims_api.operations import waterlog
>>> client = SlimsClient()

Get mouse information
>>> mouse, weight_records, water_restriction = fetch_waterlog_models(client,"000000")

Switch to adlib
>>> if mouse.water_restricted:
...     switch_to_adlib_water(client,mouse)

Write waterlog results
>>> for i in range(3):
...     write_waterlog_result(
...         client,
...         date=datetime.datetime.now(),
...         weight_g=20+i,
...         water_earned_ml=0.5,
...         water_supplement_delivered_ml=1,
...         water_supplement_recommended_ml=1,
...         comments=f"Test {i+1}",
...     )

Switch to water restricted
>>> switch_to_water_restricted(client,mouse,target_weight_fraction=0.86)

Update target weight fraction
>>> update_target_weight_fraction(client,mouse,0.9)

"""

from datetime import datetime
from typing import Optional

from aind_slims_api import models, SlimsClient, exceptions
from aind_slims_api.models import (
    SlimsMouseContent,
    SlimsWaterlogResult,
    SlimsWaterRestrictionEvent,
)


def fetch_waterlog_models(
    client: SlimsClient,
    mouse_barcode: str,
) -> tuple[
    SlimsMouseContent,
    list[SlimsWaterlogResult],
    SlimsWaterRestrictionEvent | None,
]:
    """Fetches information relating to weight/water logs for a given mouse from SLIMS

    Examples
    --------
    >>> from aind_slims_api import SlimsClient
    >>> client = SlimsClient()
    >>> mouse, weight_records, water_restriction = fetch_waterlog_models(client,"000000")
    """
    mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse_barcode)

    waterlog_results = client.fetch_models(
        models.SlimsWaterlogResult,
        mouse_pk=mouse.pk,
        sort=["date"],
    )

    if mouse.water_restricted:
        restriction = client.fetch_model(
            models.SlimsWaterRestrictionEvent,
            mouse_pk=mouse.pk,
            sort=["start_date"],
        )
    else:
        restriction = None

    return mouse, waterlog_results, restriction


def calculate_suggested_water(
    weight: float,
    target: float,
    earned: float,
    minimum: float,
    maximum: float,
) -> float:
    """Calculates supplemental water to give the mouse to achieve target weight.

    Earned water affects min/max, but is assumed to already be factored into the measured weight.

    Examples
    --------

    >>> test_cases = [
    ...     (21, 23, 0, 1, 3.5, 2),
    ...     (21, 23, 0.5, 1, 3.5, 2),
    ...     (21, 23, 1, 1, 3.5, 2),
    ...     (18, 23, 0, 1, 3.5, 3.5),
    ...     (18, 23, 2, 1, 3.5, 1.5),
    ...     (18, 23, 5, 1, 3.5, 0),  # earned more than max
    ...     (25, 23, 0, 1, 3.5, 1),
    ...     (25, 23, 0.5, 1, 3.5, 0.5),
    ...     (25, 23, 1.5, 1, 3.5, 0),
    ... ]
    >>> for (weight,target,earned,min,max,expected) in test_cases:
    ...     suggestion = calculate_suggested_water(weight,target,earned,min,max)
    ...     if not suggestion == expected:
    ...         print(f'Fails for {(weight,target,earned,min,max,expected)}')
    """
    # Water needed to achieve target weight
    weight_difference = max(0, target - weight)
    # Don't suggest less than the daily min
    supplement = max(weight_difference, minimum - earned)
    # Don't suggest more than the daily max
    supplement = min(supplement, maximum - earned)
    # Don't suggest less than 0
    supplement = max(supplement, 0)
    return supplement


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
        mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse)

    if water_restriction_event is None:
        water_restriction_event = client.fetch_model(
            models.SlimsWaterRestrictionEvent,
            mouse_pk=mouse.pk,
        )

    if mouse.baseline_weight_g is None:
        raise exceptions.SlimsAPIException(
            "Mouse has no baseline weight, cannot calculate water suggestion."
        )

    suggested = calculate_suggested_water(
        current_weight,
        mouse.baseline_weight_g * water_restriction_event.target_weight_fraction,
        earned_water,
        minimum,
        maximum,
    )

    return suggested


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
        mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse)

    test_pk = client.fetch_pk(
        "Test", test_name="test_waterlog"
    )  # TODO: Explain why SLIMS needs this

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


def post_baseline_weight(
    client: SlimsClient,
    mouse: str | models.SlimsMouseContent,
    new_baseline_weight: float,
):
    """Update the baseline weight in SLIMS and self.mouse"""

    if isinstance(mouse, str):
        mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse)

    mouse.baseline_weight_g = new_baseline_weight
    mouse = client.update_model(mouse, "baseline_weight")
    # logger.info(
    #     f"Updated mouse {self.mouse_name} " f"baseline weight to {new_baseline_weight}"
    # )


def switch_to_water_restricted(
    client: SlimsClient,
    mouse: str | models.SlimsMouseContent,
    user: str | models.SlimsUser,
    target_weight_fraction: float,
):
    """If the mouse is on ad-lib water,
    - Create a water restriction event starting today
    - Update the mouse's water_restricted field
    - Update SLIMS with the above
    - Update local data accordingly"""

    if isinstance(mouse, str):
        mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse)
    if isinstance(user, str):
        user = client.fetch_model(models.SlimsUser, username=user)

    if mouse.water_restricted:
        # logger.info("Mouse is already water restricted")
        return

    wrest_pk = client.fetch_pk(
        "ContentEventType",
        cnvt_uniqueIdentifier="cnvt_water_restriction",
    )

    new_restriction = models.SlimsWaterRestrictionEvent(
        cnvn_cf_assignedBy=user.full_name,
        cnvn_cf_targetWeightFraction=target_weight_fraction,
        cnvn_fk_content=mouse.pk,
        cnvn_fk_contentEventType=wrest_pk,
    )
    mouse.water_restricted = True
    mouse = client.update_model(mouse, "water_restricted")

    restriction = client.add_model(new_restriction)
    # all_restrictions.append(restriction)
    # logger.info(f"Switched mouse {self.mouse_name} to Water Restricted")
    return restriction


def switch_to_adlib_water(
    client: SlimsClient,
    mouse: str | models.SlimsMouseContent,
):
    """If the mouse is water restricted,
    - Set the end date of the active restriction event to today
    - Update the mouse's water_restricted field
    - Update SLIMS with the above
    - Update local data accordingly"""

    if isinstance(mouse, str):
        mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse)

    if not mouse.water_restricted:
        # logger.info("Mouse is already on ad-lib water")
        return

    restriction = client.fetch_model(
        models.SlimsWaterRestrictionEvent,
        mouse_pk=mouse.pk,
        sort="start_date",
    )

    # update model
    mouse.water_restricted = False
    mouse = client.update_model(mouse, "water_restricted")

    # update restriction with end date
    restriction.end_date = datetime.now()
    restriction = client.update_model(restriction, "end_date")
    # logger.info(f"Switched mouse {self.mouse_name} to Adlib Water")


def update_target_weight_fraction(
    client: SlimsClient,
    mouse: str | models.SlimsMouseContent,
    new_twf: float,
):
    """Update the target weight fraction of the active restriction"""
    if not mouse.water_restricted:
        # logger.info("Mouse is not water restricted")
        return

    if isinstance(mouse, str):
        mouse = client.fetch_model(models.SlimsMouseContent, barcode=mouse)

    restriction = client.fetch_model(
        models.SlimsWaterRestrictionEvent,
        mouse_pk=mouse.pk,
        sort="start_date",
    )

    restriction.target_weight_fraction = new_twf
    restriction = client.update_model(restriction, "target_weight_fraction")
    # logger.info(
    #     f"Updated mouse {self.mouse_name} " f"target weight fraction to {new_twf}"
    # )
