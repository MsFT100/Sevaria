# payments/pesapalOath.py
import requests
from django.conf import settings


def get_access_token():
    url = settings.PESAPAL_LIVE_URL  # Use the correct URL for sandbox or production
    consumer_key = settings.PESAPAL_CONSUMER_KEY
    consumer_secret = settings.PESAPAL_CONSUMER_SECRET

    
    payload = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('token')  # Use the correct field name for the access token
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining access token: {e}")
        return None
