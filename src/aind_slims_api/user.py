import logging
from typing import Annotated, Optional

from pydantic import Field, ValidationError

from .core import SlimsBaseModel, SlimsClient, UnitSpec

logger = logging.getLogger()


# TODO: Tighten this up once users are more commonly used
class SlimsUser(SlimsBaseModel):
    username: str = Field(..., alias="user_userName")
    first_name: Optional[str] = Field("", alias="user_firstName")
    last_name: Optional[str] = Field("", alias="user_lastName")
    full_name: Optional[str] = Field("", alias="user_fullName")
    email: Optional[str] = Field("", alias="user_email")
    pk: int = Field(..., alias="user_pk")

    _slims_table: str = "User"


def fetch_user(
    client: SlimsClient,
    username: str,
) -> SlimsUser:
    """Fetches user information for a user with username {username}"""
    users = client.fetch(
        "User",
        user_userName=username,
    )

    if len(users) > 0:
        user_details = users[0]
        if len(users) > 1:
            logger.warning(
                f"Warning, Multiple users in SLIMS with username {users}, using pk={user_details.pk}"
            )
    else:
        logger.warning("Warning, User not in SLIMS")
        return

    try:
        mouse = SlimsUser.model_validate(user_details)
    except ValidationError as e:
        logger.error(f"SLIMS data validation failed, {repr(e)}")
        return

    return mouse
