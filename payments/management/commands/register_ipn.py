# yourapp/management/commands/register_ipn.py
import requests
from django.core.management.base import BaseCommand
from payments.pesapalOath import get_access_token
from django.conf import settings

class Command(BaseCommand):
    help = 'Register IPN URL with Pesapal'
    
    def handle(self, *args, **options):
        token = get_access_token()  # Call the function with parentheses
        if not token:
            self.stdout.write(self.style.ERROR('Failed to get access token.'))
            return
        
        url = settings.PESAPAL_IPN_URL  # Ensure this is the correct URL
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = {
            'url': 'https://10f1-41-212-45-223.ngrok-free.app/api/payments/ipn/',  # Your IPN URL
            'ipn_notification_type': 'POST',
        }
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS("IPN URL registered successfully."))
            self.stdout.write(str(response.json()))
        else:
            self.stdout.write(self.style.ERROR("Failed to register IPN URL."))
            self.stdout.write(response.text)
