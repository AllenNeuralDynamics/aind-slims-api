"""Models for abstractions around Slims records. Friendlier names and
 documenation on how things relate to each other in our specific instance.
"""

from aind_slims_api.models.attachment import SlimsAttachment
from aind_slims_api.models.behavior_session import SlimsBehaviorSession
from aind_slims_api.models.instrument import SlimsInstrument
from aind_slims_api.models.metadata import SlimsMetadataReference
from aind_slims_api.models.mouse import SlimsMouseContent
from aind_slims_api.models.unit import SlimsUnit
from aind_slims_api.models.user import SlimsUser
from aind_slims_api.models.waterlog_result import SlimsWaterlogResult
from aind_slims_api.models.waterlog_water_restriction import SlimsWaterRestrictionEvent

__all__ = [
    "SlimsAttachment",
    "SlimsBehaviorSession",
    "SlimsInstrument",
    "SlimsMouseContent",
    "SlimsUnit",
    "SlimsUser",
    "SlimsWaterlogResult",
    "SlimsWaterRestrictionEvent",
    "SlimsMetadataReference",
]
