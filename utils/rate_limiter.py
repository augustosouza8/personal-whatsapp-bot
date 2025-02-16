# utils/rate_limiter.py
"""
Rate Limiter Module

This module implements a basic in-memory rate limiting mechanism to control the number
of messages a user can send within a given time frame.
"""

import time
import logging
from config import settings

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# Dictionary to store lists of timestamps for each user's messages.
user_message_timestamps = {}

def is_rate_limited(user_id: str) -> bool:
    """
    Check if a user has exceeded the rate limit.

    Args:
        user_id (str): Unique identifier for the user (e.g., their WhatsApp number).

    Returns:
        bool: True if the user is rate limited, False otherwise.
    """
    current_time = time.time()
    # Retrieve the list of timestamps for this user, defaulting to an empty list.
    timestamps = user_message_timestamps.get(user_id, [])
    # Keep only timestamps within the last hour (3600 seconds).
    timestamps = [timestamp for timestamp in timestamps if current_time - timestamp < 3600]
    user_message_timestamps[user_id] = timestamps

    logger.debug("Current rate for user %s: %s", user_id, user_message_timestamps[user_id])

    # If the number of messages in the past hour reaches or exceeds the limit, rate limit the user.
    if len(timestamps) >= settings.DEFAULT_RATE_LIMIT_PER_HOUR:
        return True

    # Otherwise, record the current timestamp and allow the message.
    timestamps.append(current_time)
    user_message_timestamps[user_id] = timestamps
    return False
