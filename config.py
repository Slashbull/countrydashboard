# config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

# =============================================================================
# APPLICATION CREDENTIALS
# =============================================================================
# Set these to secure values in production.
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin123")

# =============================================================================
# GOOGLE SHEET SETTINGS
# =============================================================================
# Default sheet name to use when accessing a Google Sheet.
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "data")

# Permanent Google Sheet link configuration:
# If the environment variable PERMANENT_GOOGLE_SHEET_LINK is set and non‑empty,
# the app will automatically load data from this link.
PERMANENT_GOOGLE_SHEET_LINK = os.getenv(
    "PERMANENT_GOOGLE_SHEET_LINK",
    "https://docs.google.com/spreadsheets/d/1wPnhCLcwNwlOC-3YW3ku0SLwDz9vYghr-HgR6yEtWBk/edit?usp=sharing"
).strip()
USE_PERMANENT_GOOGLE_SHEET_LINK = bool(PERMANENT_GOOGLE_SHEET_LINK)

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
# Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# =============================================================================
# CACHE AND PERFORMANCE SETTINGS
# =============================================================================
# Maximum number of entries for streamlit caching (if used)
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "100"))

# =============================================================================
# FORECASTING SETTINGS
# =============================================================================
# Window size (number of periods) for rolling average or forecasting models
FORECASTING_WINDOW = int(os.getenv("FORECASTING_WINDOW", "3"))

# =============================================================================
# API KEYS & OTHER INTEGRATIONS
# =============================================================================
# Example: API key for a climate data provider (if needed)
OPEN_METEO_API_KEY = os.getenv("OPEN_METEO_API_KEY", "")

# =============================================================================
# SUMMARY:
# This configuration file centralizes credentials, external data source settings,
# logging levels, caching, and other parameters. Make sure to secure sensitive
# information and adjust these parameters to fit your deployment environment.
# =============================================================================
