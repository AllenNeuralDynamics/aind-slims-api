import unittest

from aind_slims_api.configuration import AindSlimsApiSettings
from aind_slims_api.waterlog import WaterlogSlimsClient


class TestWaterlogClient(unittest.TestCase):
    """Example Test Class"""

    def test_fetch_mouse(self):
        wl_client = WaterlogSlimsClient()
        wl_client.fetch_mouse_info("614173")
        pass

    # @pytest.mark.parametrize("mouse_name", ["614173"])
    # def test_waterlog(mouse_name):
    #     wlclient = WaterlogSlimsClient()
    #     wlclient.fetch_mouse_info(mouse_name)


if __name__ == "__main__":
    unittest.main()
