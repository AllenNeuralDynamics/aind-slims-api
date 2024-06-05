""" Tests waterlog models, methods, and Mouse class"""

import unittest

from aind_slims_api import SlimsClient
from aind_slims_api.waterlog import Mouse
from aind_slims_api.user import SlimsUser


class TestWaterlog(unittest.TestCase):
    """Example Test Class"""

    def setup(self):
        """set client, user, and test_mouse_id"""
        self.client = SlimsClient()
        # self.user = fetch_user(client, "SIPE")
        self.user = SlimsUser(
            user_userName="test",
            user_fullName="test mctesterson",
            user_pk=8000,
        )
        self.test_mouse_id = "614173"

    def test_main_sequence_using_mouse_object(self):
        """Runs through waterlog methods"""
        self.setup()

        mouse = Mouse(
            self.test_mouse_id, user=self.user, slims_client=self.client
        )

        if mouse.mouse.water_restricted:
            mouse.switch_to_adlib_water()

        # Make some waterlog entries
        for i in range(3):
            mouse.add_waterlog_record(
                weight=20 + i,
                water_earned=0.5,
                water_supplement_recommended=1,
                water_supplement_delivered=1,
                comments=f"Test {i}",
            )

        # Post baseline weight
        mouse.post_baseline_weight(21)

        # Water restrict
        mouse.switch_to_water_restricted(target_weight_fraction=0.86)

        # Add another waterlog result
        mouse.add_waterlog_record(
            weight=20,
            water_earned=0.5,
            water_supplement_recommended=1,
            water_supplement_delivered=1,
            comments=f"Test {i+1}",
        )

        # Update target weight fraction
        mouse.update_target_weight_fraction(0.9)

        # Switch to adlib
        mouse.switch_to_adlib_water()


# class TestPydanticModels(unittest.TestCase):
#     def test_slimsmousecontent(self):
#         mouse = SLIMSMouseContent(
#             cntn_cf_baseline_weight=50,
#             cntn_cf_scientificPointOfContact="me",
#             cntn_cf_waterRestricted=False,
#             cntn_pk=9000,
#         )


if __name__ == "__main__":
    unittest.main()
