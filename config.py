# config.py
APP_TITLE = "Trade Data Dashboard"

# Single-user credentials (for demonstration only; use hashed passwords in production)
SINGLE_USER = {
    "username": "admin",
    "password": "admin_password",  # Plaintext for demo only
    "name": "Admin User"
}

# Default sheet name for Google Sheets uploads
DEFAULT_SHEET_NAME = "Sheet1"

# (Optional) Open-Meteo API settings (modify as needed)
OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"
