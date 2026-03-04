"""
============================================
AutoHire AI - Configuration Module
============================================
Centralizes all configuration using environment variables.
Uses python-dotenv for loading .env file values.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Application configuration class.
    All settings are loaded from environment variables with sensible defaults.
    """

    # ----- Database Configuration -----
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'autohire_ai')

    # ----- Email Configuration -----
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER', '')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
    EMAIL_RECIPIENT = os.getenv('EMAIL_RECIPIENT', '')

    # ----- Flask Configuration -----
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'autohire-secret-key-change-me')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))

    # ----- Scraping Configuration -----
    SCRAPE_ROLE = os.getenv('SCRAPE_ROLE', 'Software Engineer')
    SCRAPE_LOCATION = os.getenv('SCRAPE_LOCATION', 'India')
    SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 12))
    CHROME_HEADLESS = os.getenv('CHROME_HEADLESS', 'True').lower() == 'true'

    @classmethod
    def get_db_uri(cls):
        """Build MySQL connection URI for SQLAlchemy."""
        return (
            f"mysql+mysqlconnector://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )

    @classmethod
    def validate(cls):
        """Validate that required configuration values are set."""
        errors = []
        if not cls.DB_PASSWORD:
            errors.append("DB_PASSWORD is not set")
        if not cls.EMAIL_USER:
            errors.append("EMAIL_USER is not set")
        if not cls.EMAIL_PASSWORD:
            errors.append("EMAIL_PASSWORD is not set")
        if not cls.EMAIL_RECIPIENT:
            errors.append("EMAIL_RECIPIENT is not set")
        return errors
