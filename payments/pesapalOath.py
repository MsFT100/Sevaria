import requests
from django.conf import settings
import base64

def get_access_token():
    url = settings.PESAPAL_SANDBOX_URL
    consumer_key = settings.PESAPAL_CONSUMER_KEY
    consumer_secret = settings.PESAPAL_CONSUMER_SECRET

    # Encode the consumer key and secret
    credentials = f"{consumer_key}:{consumer_secret}"
    encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['token']  # Assuming the response contains a 'token' field
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining access token: {e}")
        return None