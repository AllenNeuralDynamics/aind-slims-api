"""Contains a model for a user, and a method for fetching it"""

import logging
from typing import Optional

from aind_slims_api.core import SlimsClient

logger = logging.getLogger()


def fetch_user(
    client: SlimsClient,
    username: str,
) -> Optional[dict]:
    """Fetches user information for a user with username {username}"""
    users = client.fetch(
        "User",
        user_userName=username,
    )

    if len(users) > 0:
        user_details = users[0]
        if len(users) > 1:
            logger.warning(
                f"Warning, Multiple users in SLIMS with "
                f"username {[u.json_entity for u in users]}, "
                f"using pk={user_details.pk()}"
            )
    else:
        logger.warning("Warning, User not in SLIMS")
        user_details = None

    return None if user_details is None else user_details.json_entity
