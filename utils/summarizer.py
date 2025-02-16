# utils/summarizer.py
"""
Conversation Summarizer Module

This module manages a summarized conversation context for each user.
Instead of storing the full conversation history, a summary is maintained which is updated
after every few new user messages. This approach reduces storage overhead while still retaining
essential context for generating responses.

Database Schema (collection: "conversation_summaries"):
    - user_id: Unique identifier for the user.
    - summary: Current conversation summary text.
    - unsummarized_count: Number of new messages since the last summary update.
    - buffer: Concatenated new interactions not yet incorporated into the summary.
"""

import time
import logging
from core.database import get_db
from core.llm import get_llm_response

# Initialize a logger for this module
logger = logging.getLogger(__name__)

# Define the threshold for the number of messages before updating the summary.
UPDATE_THRESHOLD = 3

def update_summary(user_id: str, new_message: str, role: str = "User") -> str:
    """
    Update the conversation summary for a user with a new interaction.

    Args:
        user_id (str): Unique identifier for the user.
        new_message (str): The new message text to incorporate.
        role (str): Role of the sender ("User" or "Bot").

    Returns:
        str: The updated conversation summary after processing the new message.
    """
    db = get_db()
    # Access the 'conversation_summaries' collection from the database.
    collection = db.conversation_summaries

    # Attempt to retrieve an existing summary record for the user.
    record = collection.find_one({"user_id": user_id})
    if not record:
        # If no record exists, create a new one with default values.
        record = {
            "user_id": user_id,
            "summary": "",
            "unsummarized_count": 0,
            "buffer": ""
        }
        collection.insert_one(record)

    # Append the new message to the buffer, prefixed by the sender's role.
    new_entry = f"{role}: {new_message}\n"
    updated_buffer = record.get("buffer", "") + new_entry

    # Increment the unsummarized message count if the message is from the user.
    unsummarized_count = record.get("unsummarized_count", 0)
    if role == "User":
        unsummarized_count += 1

    # Prepare fields to update in the database.
    update_fields = {
        "buffer": updated_buffer,
        "unsummarized_count": unsummarized_count,
        "last_updated": time.time()
    }

    # If the unsummarized count meets or exceeds the threshold, update the summary.
    if unsummarized_count >= UPDATE_THRESHOLD:
        logger.info("Threshold reached for user %s (%s messages). Updating summary.", user_id, unsummarized_count)
        current_summary = record.get("summary", "")
        # Construct a prompt that instructs the LLM to generate an updated summary.
        prompt = (
            "You are tasked with summarizing the conversation between a user and a bot. "
            "Below is the current summary and the new interactions since the last summary update. "
            "Generate an updated, concise summary that captures all key points and changes in context.\n"
            f"Current Summary: {current_summary}\n"
            f"New Interactions: {updated_buffer}\n"
            "Output only the new summary text."
        )
        try:
            # Generate the new summary using the LLM.
            new_summary = get_llm_response(prompt)
            update_fields["summary"] = new_summary
            update_fields["unsummarized_count"] = 0
            update_fields["buffer"] = ""
            updated_summary = new_summary
            logger.info("Summary updated for user %s.", user_id)
        except Exception as e:
            # If LLM fails, retain the existing summary.
            updated_summary = current_summary
            logger.error("Failed to update summary for user %s. Keeping existing summary.", user_id, exc_info=True)
    else:
        updated_summary = record.get("summary", "")
        logger.info("Summary not updated for user %s. Unsummarized count: %s", user_id, unsummarized_count)

    # Update the record in the database with the new summary data.
    collection.update_one({"user_id": user_id}, {"$set": update_fields})
    return updated_summary
