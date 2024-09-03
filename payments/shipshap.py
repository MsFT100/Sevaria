import requests
from django.conf import settings

def get_shipping_rates(address_from, address_to, parcels):
    url = "https://api.shipshap.com/v1/shipments/"
    payload = {
        "address_from": address_from,
        "address_to": address_to,
        "parcels": parcels,
        "is_test": True  # Set to False in production
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Token {settings.SHIPSHAP_API_TOKEN}"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
