import datetime
from aind_slims_api import SlimsClient
from aind_slims_api.waterlog import Mouse
from aind_slims_api.user import SlimsUser, fetch_user


def main_sequence_using_mouse_object(client: SlimsClient, mouse_id: str):
    # user = fetch_user(client, "SIPE")
    user = SlimsUser(
        user_userName="test", user_fullName="test mctesterson", user_pk=8000
    )
    mouse = Mouse(mouse_id, user=user, slims_client=client)

    if mouse.mouse.water_restricted:
        mouse.switch_to_adlib_water()

    ## Make some waterlog entries
    for i in range(3):
        mouse.add_waterlog_record(
            weight=20 + i,
            water_earned=0.5,
            water_supplement_recommended=1,
            water_supplement_delivered=1,
            comments=f"Test {i}",
        )

    ## Post baseline weight
    mouse.post_baseline_weight(21)

    ## Water restrict
    mouse.switch_to_water_restricted(target_weight_fraction=0.86)

    ## Add another waterlog result
    mouse.add_waterlog_record(
        weight=20,
        water_earned=0.5,
        water_supplement_recommended=1,
        water_supplement_delivered=1,
        comments=f"Test {i+1}",
    )

    ## Update target weight fraction
    mouse.update_target_weight_fraction(0.9)

    ## Switch to adlib
    mouse.switch_to_adlib_water()


if __name__ == "__main__":
    mouse_id = "614173"
    client = SlimsClient()

    main_sequence_using_mouse_object(client, mouse_id)

    pass
