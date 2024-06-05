from typing import Optional

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings


class AindSlimsApiSettings(BaseSettings):
    """Settings for SLIMS Client

    Per pydantic-settings docs https://docs.pydantic.dev/latest/concepts/pydantic_settings/
    Loads slims credentials from environment variables if present"""

    slims_url: str = "https://aind-test.us.slims.agilent.com/slimsrest/"
    slims_username: str = ""
    slims_password: SecretStr = ""

    wl_default_target_weight_fraction: float = 0.85
    wl_min_target_weight_fraction: float = 0.75
    wl_max_target_weight_fraction: float = 1.0
