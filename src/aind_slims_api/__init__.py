"""Init package"""

__version__ = "0.0.0"

from .configuration import AindSlimsApiSettings

config = AindSlimsApiSettings()

from .core import SlimsClient  # noqa
