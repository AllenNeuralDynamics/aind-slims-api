"""Init package"""

__version__ = "0.1.2"

from aind_slims_api.configuration import AindSlimsApiSettings

config = AindSlimsApiSettings()

from aind_slims_api.core import SlimsClient  # noqa
