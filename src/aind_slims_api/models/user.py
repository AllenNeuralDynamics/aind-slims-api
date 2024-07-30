"""Contains a model for a user."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


# TODO: Tighten this up once users are more commonly used
class SlimsUser(SlimsBaseModel):
    """Model for user information in SLIMS

    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> user = client.fetch_model(SlimsUser, username="LKim")
    """

    username: str = Field(
        ...,
        serialization_alias="user_userName",
        validation_alias="user_userName",
    )
    first_name: Optional[str] = Field(
        "",
        serialization_alias="user_firstName",
        validation_alias="user_firstName",
    )
    last_name: Optional[str] = Field(
        "",
        serialization_alias="user_lastName",
        validation_alias="user_lastName",
    )
    full_name: Optional[str] = Field(
        "",
        serialization_alias="user_fullName",
        validation_alias="user_fullName",
    )
    email: Optional[str] = Field(
        "",
        serialization_alias="user_email",
        validation_alias="user_email",
    )
    pk: int = Field(
        ...,
        serialization_alias="user_pk",
        validation_alias="user_pk",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="user_createdOn",
        validation_alias="user_createdOn",
    )

    _slims_table = "User"
