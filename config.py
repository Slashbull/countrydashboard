# config.py
# Configuration settings and constants

APP_TITLE = "Trade Data Dashboard"

# Data paths (modify as needed)
DATA_FILE = "data/trade_data.csv"  # if using a static file

# Authentication credentials: (For demonstration only. In production, use environment variables or a secure store.)
AUTH_CREDENTIALS = {
    "usernames": {
        "admin": {
            "name": "Admin User",
            "password": "admin_password"  # In practice, store hashed passwords
        },
        "user": {
            "name": "Regular User",
            "password": "user_password"
        }
    }
}
