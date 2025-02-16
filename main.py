# main.py
"""
Main entry point for the LLM-Powered WhatsApp Bot using Twilio and Flask.

This application listens for incoming WhatsApp messages via Twilio's webhook,
processes them with our LLM-powered message handler, and sends a response back
to the sender using Twilio's messaging API.

Key functionalities:
    - Exposes a /webhook endpoint to receive POST requests from Twilio.
    - Extracts sender information and message content from incoming requests.
    - Applies rate limiting to prevent abuse.
    - Delegates message processing to our message handler.
    - Sends generated responses back to the sender via Twilio.
    - Implements robust error handling and logging for debugging.
    - Ensures the phone number is properly formatted using a format check.
"""

import logging
from flask import Flask, request, jsonify
from handlers import message as message_handler  # Module for processing messages
from utils import rate_limiter  # Module for in-memory rate limiting
from twilio.rest import Client  # Twilio's Python SDK for sending messages
from config import settings  # Configuration settings
import os

# Initialize the Flask application
app = Flask(__name__)

# Configure logging to include timestamps, module names, log levels, and messages
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize the Twilio client using credentials from the configuration
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def format_phone_number(phone_number: str) -> str:
    """
    Ensure the phone number is in the correct WhatsApp format: "whatsapp:+{number}".

    This function trims any whitespace, ensures the number starts with "whatsapp:",
    and removes any spaces in the number portion. If the number after the prefix does
    not start with a '+', it will add one.

    Args:
        phone_number (str): The phone number to format.

    Returns:
        str: The formatted phone number.
    """
    # Remove leading/trailing whitespace from the entire input.
    phone_number = phone_number.strip()

    # Ensure the phone number starts with "whatsapp:".
    if not phone_number.startswith("whatsapp:"):
        phone_number = "whatsapp:" + phone_number

    # Get the part of the number after "whatsapp:" and remove any spaces.
    prefix_length = len("whatsapp:")
    number_without_prefix = phone_number[prefix_length:].strip().replace(" ", "")

    # If the number doesn't start with '+', add it.
    if not number_without_prefix.startswith("+"):
        number_without_prefix = "+" + number_without_prefix

    # Return the properly formatted number.
    formatted = "whatsapp:" + number_without_prefix
    return formatted


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint to handle incoming WhatsApp messages from Twilio.

    This endpoint:
      - Extracts the sender's number and message text from the incoming request.
      - Checks for cases where the message body is missing and ignores those events.
      - Ignores messages that originate from the bot's own Twilio WhatsApp number.
      - Applies rate limiting to avoid abuse.
      - Processes the message via the message handler.
      - Sends the generated response back to the sender using Twilio.
    """
    try:
        # Twilio sends data as URL-encoded form data by default.
        data = request.form

        # Extract sender's phone number and the message content.
        user_id = data.get('From')
        message_text = data.get('Body')

        # Log the received message details.
        app.logger.info("Received message from %s: %s", user_id, message_text)

        # Ignore webhook events that do not include a message body.
        if message_text is None:
            app.logger.warning("Ignoring webhook event with no message body from %s", user_id)
            return jsonify({"status": "ignored"}), 200

        # Ignore messages coming from our own Twilio WhatsApp number.
        if user_id == settings.TWILIO_WHATSAPP_NUMBER:
            app.logger.warning("Ignoring message from our own Twilio number: %s", user_id)
            return jsonify({"status": "ignored"}), 200

        # Apply rate limiting to prevent abuse.
        if rate_limiter.is_rate_limited(user_id):
            app.logger.warning("User %s is rate limited.", user_id)
            return jsonify({"status": "rate_limited"}), 429

        # Process the message using our message handler.
        response_text = message_handler.process_message(message_text, user_id)

        # Send the generated response back via Twilio.
        send_whatsapp_message(user_id, response_text)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        # Log any errors encountered during processing.
        app.logger.error("Error processing webhook: %s", str(e), exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


def send_whatsapp_message(to_number: str, message_body: str):
    """
    Sends a WhatsApp message using Twilio's API.

    Args:
        to_number (str): The recipient's phone number, which should be in the format "whatsapp:+{number}".
        message_body (str): The text content to send.

    This function first ensures that the phone number is correctly formatted before
    sending the message using the Twilio client.
    """
    try:
        # Format the phone number to ensure it's in the correct format.
        formatted_to_number = format_phone_number(to_number)

        # Create and send the message using Twilio's messaging service.
        message = twilio_client.messages.create(
            body=message_body,
            from_=settings.TWILIO_WHATSAPP_NUMBER,  # Your Twilio WhatsApp-enabled number
            to=formatted_to_number
        )
        app.logger.info("Sent message to %s with SID: %s", formatted_to_number, message.sid)
    except Exception as e:
        # Log any errors encountered during the sending process.
        app.logger.error("Failed to send WhatsApp message to %s: %s", to_number, str(e), exc_info=True)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)

