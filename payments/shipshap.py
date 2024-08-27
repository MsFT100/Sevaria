import requests
from django.conf import settings

def create_shipment(order):
    url = 'https://api.shipshap.com/v1/shipments'  # Replace with the actual ShipShap API URL
    headers = {
        'Authorization': f'Bearer {settings.SHIPSHAP_API_KEY}',  # Use your API key
        'Content-Type': 'application/json'
    }
    payload = {
        'origin': {
            'name': 'Your Company',
            'address': '123 Your Street',
            'city': 'Your City',
            'postal_code': '12345',
            'country': 'KE',
            'phone': '+254700000000',
        },
        'destination': {
            'name': order.customer_name,
            'address': order.shipping_address,
            'city': order.shipping_city,
            'postal_code': order.shipping_postal_code,
            'country': order.shipping_country,
            'phone': order.phone_number,
        },
        'package': {
            'weight': 1.5,  # Adjust based on your product
            'dimensions': {
                'length': 10,
                'width': 5,
                'height': 5
            }
        },
        'carrier': 'preferred_carrier'  # You can specify the carrier or let ShipShap choose
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201:
        shipment_data = response.json()
        return shipment_data
    else:
        # Handle error
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
