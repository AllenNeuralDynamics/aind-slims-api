"""Contains a model for the instrument content, and a method for fetching it"""

from datetime import datetime
from typing import ClassVar, Optional

from pydantic import Field

from aind_slims_api.models.base import SlimsBaseModel


class SlimsInstrumentRdrc(SlimsBaseModel):
    """Model for Instrument Rdrc"""

    pk: Optional[int] = Field(
        default=None, serialization_alias="rdrc_pk", validation_alias="rdrc_pk"
    )
    name: Optional[str] = Field(
        default=None, serialization_alias="rdrc_name", validation_alias="rdrc_name"
    )
    created_on: Optional[datetime] = Field(
        default=None,
        serialization_alias="rdrc_createdOn",
        validation_alias="rdrc_createdOn",
    )
    _slims_table = "ReferenceDataRecord"
    _base_fetch_filters: ClassVar[dict[str, str]] = {
        "rdty_name": "AIND Instruments",
    }


class SlimsInstrument(SlimsBaseModel):
    """Model for a SLIMS instrument record.
    This model may be deprecated. Use SlimsInstrumentRdrc for newer instruments.
    Examples
    --------
    >>> from aind_slims_api.core import SlimsClient
    >>> client = SlimsClient()
    >>> instrument = client.fetch_model(SlimsInstrument, name="323_EPHYS1_OPTO")
    """

    # can't use alias for this due to https://github.com/pydantic/pydantic/issues/5893
    name: str = Field(
        ...,
        serialization_alias="nstr_name",
        validation_alias="nstr_name",
        description="The name of the instrument",
    )
    pk: Optional[int] = Field(
        default=None,
        serialization_alias="nstr_pk",
        validation_alias="nstr_pk",
    )
    created_on: Optional[datetime] = Field(
        None,
        serialization_alias="nstr_createdOn",
        validation_alias="nstr_createdOn",
    )
    _slims_table = "Instrument"

    # todo add more useful fields
