"""Init package"""

from .core import SlimsClient  # noqa


__version__ = "0.0.0"

from .configuration import AindSlimsApiSettings

config = AindSlimsApiSettings()
