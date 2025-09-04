import requests
from auth import refresh_access_token

ZOHO_API_DOMAIN = "https://www.zohoapis.com"


def create_lead(lead_data: dict):
    """
    Creates a lead in Zoho CRM with the given dictionary of lead fields.
    """
    access_token = refresh_access_token()
    if not access_token:
        return {"error": "Could not refresh access token"}

    url = f"{ZOHO_API_DOMAIN}/crm/v2/Leads"
    headers = {"Authorization": f"Zoho-oauthtoken {access_token}"}
    payload = {"data": [lead_data]}

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
