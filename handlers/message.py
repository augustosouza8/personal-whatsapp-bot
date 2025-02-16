# handlers/message.py
"""
Message Handler Module for the WhatsApp Bot

This module processes incoming user messages by performing the following steps:
  1. Preprocess the incoming message (e.g., trimming whitespace).
  2. Check if the message contains media request keywords and send an alert notification if needed.
  3. Update the conversation summary with the new message.
  4. Construct a prompt for the LLM by combining the conversation summary and the new message.
  5. Use the LLM integration to generate a natural, engaging response.
  6. Update the conversation summary with the bot's generated response.
  7. Return the generated response to be sent back to the user.

By separating these concerns, the code remains modular, testable, and easier to maintain.
"""

import logging
from core import llm  # LLM integration module for generating responses
from handlers import notification  # Module to send email notifications for alerts
from utils import summarizer  # Module for maintaining and updating conversation summaries

# Initialize a logger for this module
logger = logging.getLogger(__name__)

def preprocess_message(message_text: str) -> str:
    """
    Preprocess the incoming message by trimming any extra whitespace.

    If message_text is None, log a warning and return an empty string.

    Args:
        message_text (str): The original user message.

    Returns:
        str: The cleaned and preprocessed message, or an empty string if input is None.
    """
    if message_text is None:
        logger.warning("Received a message with no body in preprocess_message.")
        return ""
    return message_text.strip()

def check_media_request(message_text: str) -> bool:
    """
    Check if the message contains keywords that indicate a media request.

    Args:
        message_text (str): The message to be checked.

    Returns:
        bool: True if a media request is detected, otherwise False.
    """
    media_keywords = ["video", "photo", "voice"]
    return any(keyword in message_text.lower() for keyword in media_keywords)

def process_message(message_text: str, user_id: str) -> str:
    """
    Process an incoming message and generate an appropriate response using LLM.

    This function:
      - Preprocesses the user's message.
      - Checks for media requests and triggers an email notification if needed.
      - Updates the conversation summary with the user's new message.
      - Constructs a prompt that includes the conversation context and the latest message.
      - Calls the LLM to generate a response.
      - Updates the conversation summary with the generated response.

    Args:
        message_text (str): The text message from the user.
        user_id (str): A unique identifier for the user (typically their WhatsApp number).

    Returns:
        str: The generated response from the LLM to be sent back to the user.
    """
    # Extra check in process_message: if message_text is None, return a default response.
    if message_text is None:
        logger.warning("Received a None message_text in process_message for user %s.", user_id)
        return "I didn't catch that. Could you please repeat?"

    # Step 1: Preprocess the incoming message.
    processed_text = preprocess_message(message_text)

    # If there's no valid text after preprocessing, return a default message.
    if not processed_text:
        logger.info("No valid message text to process for user %s; returning default response.", user_id)
        return "I didn't catch that. Could you please repeat?"

    # Step 2: Check for media requests; if detected, send an alert email.
    if check_media_request(processed_text):
        subject = "Media Request Detected"
        alert_message = f"User {user_id} requested media: {processed_text}"
        notification.send_email_alert(subject, alert_message)

    # Step 3: Update the conversation summary with the user's new message.
    current_summary = summarizer.update_summary(user_id, processed_text, role="User")

    # Step 4: Construct a prompt for the LLM.
    prompt = (
        "You are engaged in a playful conversation with the user. "
        "Use the following conversation context to generate a natural and engaging reply.\n\n"
        "Conversation Summary:\n"
        f"{current_summary}\n\n"
        "User's Message:\n"
        f"{processed_text}\n\n"
        "Respond naturally while maintaining the tone of the conversation."
    )

    try:
        # Step 5: Generate a response using the LLM integration.
        response = llm.get_llm_response(prompt)
    except Exception as e:
        subject = "LLM API Failure"
        error_message = f"Error for user {user_id} with prompt: {prompt}\nError: {str(e)}"
        notification.send_email_alert(subject, error_message)
        raise e

    # Step 6: Update the conversation summary with the bot's response.
    summarizer.update_summary(user_id, response, role="Bot")
    logger.info("Updated conversation summary for user %s", user_id)

    # Step 7: Return the generated response.
    return response
