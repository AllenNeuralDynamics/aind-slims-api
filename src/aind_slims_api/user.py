"""Contains a model for a user, and a method for fetching it"""

import logging

from .core import SlimsClient

logger = logging.getLogger()


def fetch_user(
    client: SlimsClient,
    username: str,
) -> dict:
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
                f"username {users}, using pk={user_details.pk}"
            )
    else:
        logger.warning("Warning, User not in SLIMS")
        return

    return user_details
