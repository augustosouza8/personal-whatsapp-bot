# config/settings.py
"""
Configuration Settings Module for the LLM-Powered WhatsApp Bot.

This module is responsible for loading environment variables from a .env file
and defining configuration variables required by the application. By centralizing
configuration in one module, we ensure that sensitive data is not hard-coded in our source code,
making our project more secure and maintainable.

Key configurations include:
    - Twilio credentials for WhatsApp messaging.
    - Groq API key for LLM integration.
    - MongoDB URI for database connections.
    - Email credentials for sending notifications.
    - Default rate limit settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file into the system's environment
load_dotenv()

# --- LLM and Database Configuration ---

# API key for Groq, used for LLM-powered response generation
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# MongoDB URI to connect to the database (used for storing conversation summaries)
MONGODB_URI = os.getenv("MONGODB_URI")

# --- Email Notification Configuration ---

# Email address used for sending notifications (e.g., alerts for media requests or errors)
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
# Email password or app-specific password for authentication
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Rate Limiting Configuration ---

# Default number of messages allowed per hour to prevent abuse
DEFAULT_RATE_LIMIT_PER_HOUR = int(os.getenv("DEFAULT_RATE_LIMIT_PER_HOUR", 30))

# --- Twilio WhatsApp Configuration ---

# Twilio Account SID: A unique identifier for your Twilio account
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# Twilio Auth Token: Secret key used to authenticate with the Twilio API
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# Twilio WhatsApp Number: Your WhatsApp-enabled number provided by Twilio (format: "whatsapp:+1234567890")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
