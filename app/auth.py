import os
import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")

# Cache the token in memory
ACCESS_TOKEN = None


def refresh_access_token():
    """
    Refreshes Zoho OAuth access token using refresh token.
    Returns a valid access token string.
    """
    global ACCESS_TOKEN

    if ACCESS_TOKEN:  # if already cached, reuse
        return ACCESS_TOKEN

    token_url = "https://accounts.zoho.com/oauth/v2/token"
    data = {
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    }

    try:
        response = httpx.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()
        ACCESS_TOKEN = tokens.get("access_token")
        return ACCESS_TOKEN
    except Exception as e:
        print("❌ Error refreshing token:", e)
        return None
