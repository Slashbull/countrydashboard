# config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()

# =============================================================================
# Application Authentication
# =============================================================================
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin123")

# =============================================================================
# Google Sheets Configuration (for data upload)
# =============================================================================
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "data")
PERMANENT_GOOGLE_SHEET_LINK = os.getenv(
    "PERMANENT_GOOGLE_SHEET_LINK",
    "https://docs.google.com/spreadsheets/d/1wPnhCLcwNwlOC-3YW3ku0SLwDz9vYghr-HgR6yEtWBk/edit?usp=sharing"
).strip()
USE_PERMANENT_GOOGLE_SHEET_LINK = bool(PERMANENT_GOOGLE_SHEET_LINK)

# =============================================================================
# Logging and Caching Settings
# =============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")  # e.g., DEBUG, INFO, WARNING, ERROR
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", 50))

# =============================================================================
# Weather API Configuration
# =============================================================================
# API key for OpenWeather (if you choose to use it)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "94a02ef435d347d590b105838251402")

# =============================================================================
# Additional settings can be added here as needed.
# =============================================================================

