import unittest

from aind_slims_api.configuration import AindSlimsApiSettings
from aind_slims_api.core import SlimsClient
from aind_slims_api.waterlog import WaterlogSlimsClient


class TestSlimsClient(unittest.TestCase):
    """Example Test Class"""

    def test_config(self):
        config = AindSlimsApiSettings()

    def test_slims_client(self):
        client = SlimsClient()

    # @pytest.mark.parametrize("mouse_name", ["614173"])
    # def test_waterlog(mouse_name):
    #     wlclient = WaterlogSlimsClient()
    #     wlclient.fetch_mouse_info(mouse_name)


if __name__ == "__main__":
    unittest.main()
