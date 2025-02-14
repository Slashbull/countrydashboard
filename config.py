# config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (if available)
load_dotenv()

# Application credentials (change these for production)
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin123")

# Data source settings
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "data")
PERMANENT_GOOGLE_SHEET_LINK = os.getenv("PERMANENT_GOOGLE_SHEET_LINK", "https://docs.google.com/spreadsheets/d/1wPnhCLcwNwlOC-3YW3ku0SLwDz9vYghr-HgR6yEtWBk/edit?usp=sharing").strip()
USE_PERMANENT_GOOGLE_SHEET_LINK = bool(PERMANENT_GOOGLE_SHEET_LINK)

# Performance & caching settings
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "100"))
FORECASTING_WINDOW = int(os.getenv("FORECASTING_WINDOW", "3"))

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# (Optional) API key for future integrations
OPEN_METEO_API_KEY = os.getenv("OPEN_METEO_API_KEY", "")
