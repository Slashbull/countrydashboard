# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from a .env file

# Application credentials (secure these in production)
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin123")

# Default Google Sheet settings
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "data")

# Permanent Google Sheet Link configuration
# If the environment variable PERMANENT_GOOGLE_SHEET_LINK is set and non‑empty,
# the app will use that link automatically.
PERMANENT_GOOGLE_SHEET_LINK = os.getenv("PERMANENT_GOOGLE_SHEET_LINK", "https://docs.google.com/spreadsheets/d/1wPnhCLcwNwlOC-3YW3ku0SLwDz9vYghr-HgR6yEtWBk/edit?usp=sharing").strip()
USE_PERMANENT_GOOGLE_SHEET_LINK = bool(PERMANENT_GOOGLE_SHEET_LINK)

