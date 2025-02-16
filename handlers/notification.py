# handlers/notification.py
"""
Notification Handler Module

This module sends email notifications for events such as media requests or system errors.
"""

import logging
import smtplib
from email.mime.text import MIMEText
from config import settings

# Initialize a logger for this module
logger = logging.getLogger(__name__)

def send_email_alert(subject: str, message: str) -> None:
    """
    Send an email alert with the specified subject and message.

    Args:
        subject (str): Subject of the email.
        message (str): Message body containing details of the alert.

    This function creates and sends an email using SMTP over SSL.
    """
    try:
        # Create a MIMEText object to represent the email.
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = settings.EMAIL_SENDER  # Typically, alerts are sent to the same email.

        # Connect to the Gmail SMTP server over SSL.
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            # Log in using the email credentials from settings.
            server.login(settings.EMAIL_SENDER, settings.EMAIL_PASSWORD)
            # Send the email message.
            server.send_message(msg)
        logger.info("Email alert sent: %s", subject)
    except Exception as e:
        # Log any errors that occur during the email sending process.
        logger.error("Failed to send email alert", exc_info=True)
