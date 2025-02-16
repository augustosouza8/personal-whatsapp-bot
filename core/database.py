# core/database.py
"""
Database Connection Manager

This module establishes and manages a connection to the MongoDB database using pymongo.
It provides a function to obtain the database instance which can be used throughout the project.
"""

import logging
from pymongo import MongoClient
from config import settings
import certifi

# Initialize a logger for this module
logger = logging.getLogger(__name__)

def get_db():
    """
    Establish and return a connection to the MongoDB database.

    Returns:
        db: The MongoDB database instance.

    Raises:
        Exception: If connection to MongoDB fails.
    """
    try:
        # Create a MongoClient instance using the connection URI from settings.
        # The tlsCAFile parameter ensures that SSL certificates are verified.
        client = MongoClient(settings.MONGODB_URI, tlsCAFile=certifi.where())
        # Access a specific database; here we name it 'whatsappbotdatabase'.
        db = client['whatsappbotdatabase']
        return db
    except Exception as e:
        # Log the error details and re-raise the exception.
        logger.error("Failed to connect to MongoDB", exc_info=True)
        raise e
