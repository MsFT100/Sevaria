import json
import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
import requests
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView

from payments.send_email import send_order_confirmation, send_order_details
from payments.shipshap import get_shipping_rates
from .models import Payment
from main.models import OrderItem, Order, Product, ProductVariant
from .forms import CheckoutForm, ShippingForm

from django.core.mail import send_mail
from django.template.loader import render_to_string

from payments.pesapalOath import get_access_token  # Assuming this file contains the get_access_token function


# Admin Address
ADDRESS_FROM = {
    "name": "Jamie Kimani",
    "street1": "331 Hiilcrest Drive",
    "city": "Nairobi",
    "zip_code": "24191-00502",
    "state": "Nairobi",
    "country": "KE",
    "phone": "+254114104766",
    "email": "bryankmn@gmail.com",
    "is_test": False,
    "is_quote_only": False
}

class GetShippingRatesView(View):
    def post(self, request, *args, **kwargs):
            try:
                # Parse JSON data from request body
                data = json.loads(request.body)

                # Initialize form with parsed JSON data
                form = ShippingForm(data)

                if form.is_valid():
                    # Use form.cleaned_data to get validated fields
                    address = form.cleaned_data.get('shipping_address', '')
                    first_name = form.cleaned_data.get('first_name', '')
                    last_name = form.cleaned_data.get('last_name', '')
                    phone_number = form.cleaned_data.get('phone_number', '')
                    email = form.cleaned_data.get('email', '')
                    country = form.cleaned_data.get('country', '')
                    city = form.cleaned_data.get('city', '')
                    state = form.cleaned_data.get('state', '')
                    zip_code = form.cleaned_data.get('zip_code', '')
                    total_price = form.cleaned_data.get('total_price', '')

                    print(phone_number)
                    # Ensure total_price is a valid number
                    try:
                        total_price = float(total_price)
                    except ValueError:
                        return JsonResponse({"error": "Invalid total price"}, status=400)

                    # Define the payload for the external API
                    payload = {
                        "address_from": ADDRESS_FROM,
                        "address_to": {
                            "name": f"{first_name} {last_name}",
                            "street1": address,
                            "city": city,
                            "zip_code": zip_code,
                            "state": state,
                            "country": country,
                            "phone": phone_number,
                            "email": email,
                            "is_test": True,
                            "is_quote_only": True
                        },
                        "customs_declaration": {
                            "contents_type": "clothes",
                            "non_delivery_option": "test",
                            "certify_signer": "Sevaria",
                            "certify": True,
                            "contents_explanation": "test",
                            "items": [
                                {
                                    "weight_unit": "kg",
                                    "value_currency": "USD",
                                    "description": "clothes",
                                    "quantity": 1,
                                    "net_weight": "23",
                                    "value_amount": total_price,
                                    "origin_country": "KE",
                                    "is_test": True
                                }
                            ],
                            "incoterm": "test",
                            "eel_pfc": "test",
                            "is_test": True
                        },
                        "parcels": [
                            {
                                "weight_unit": "lb",
                                "length": "44",
                                "width": "33",
                                "height": "5",
                                "length_unit": "cm",
                                "weight": "12",
                                "is_test": True
                            }
                        ],
                        "is_test": True
                    }

                    #print(payload)
                    headers = {
                        "accept": "application/json",
                        "content-type": "application/json",
                        "Authorization": "Token test_42a045be240808dca7b9b2722a4a00b6d9c9f7f7b6c7b49203b9c5d98cf9e2e2"
                    }

                    # Make the request to ShipShap API
                    try:
                        response = requests.post("https://api.shipshap.com/v1/shipments/", json=payload, headers=headers)
                        response.raise_for_status()
                        data = response.json()
                        
                        # Extract shipping rates from the response
                        rates = data.get('rates', [])
                        print(rates)
                        return JsonResponse({"rates": rates})
                    except requests.exceptions.RequestException as e:
                        print(f"Request failed: {e}")
                        print(f"Response content: {response.content}")
                        return JsonResponse({"error": "Failed to get shipping rates"}, status=500)
                else:
                    print("Form errors:", form.errors)
                    return JsonResponse({'errors': form.errors}, status=400)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON format"}, status=400)

class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        
        #if cart is empty or invalid
        if not isinstance(cart, dict):
            return JsonResponse({'error': 'Invalid cart data format.'}, status=400)

        cart_items = []
        total_price = 0
        
        # Process each item in the cart
        for item_key, item_data in cart.items():
            product = Product.objects.get(id=item_data['product_id'])
            variant = ProductVariant.objects.get(product=product, size=item_data['size'], color=item_data['color'])

            item_total_price = product.price * item_data['quantity']
            total_price += item_total_price
            
            cart_item = {
                'product': product,
                'variant': variant,
                'quantity': item_data['quantity'],
                'price': product.price,
                'total_price': item_total_price,
            }
            cart_items.append(cart_item)


            
       
     
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
        
        }
        return render(request, 'pages/checkout.html', context)

    def post(self, request):
        form = CheckoutForm(request.POST)
        
        
        if form.is_valid():
            # Create the order instance
            order = form.save(commit=False)
            # Check if the user is authenticated, otherwise allow guest checkout
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.user = None  # Guest checkout
            
            # Retrieve cart from session
            cart = request.session.get('cart', {})
            # Debugging: Print the cart data to ensure it's as expected
            print("Cart data:", cart)
            # Initialize total price
            total_price = 0
            
            # Save the order first
            order.save()
            
            
            final_price = form.data.get('total_price', '0')
            total_price = final_price
            # Set the total price for the order
            order.total_price = total_price
            order.save()  # Save the updated order with total_price

           
            country_label = form.data.get('country', '')

            # Initiate payment with PesaPal
            token = get_access_token()
            if not token:
                return JsonResponse({'error': 'Failed to retrieve access token.'}, status=500)

            # Extract data from the form
            phone_number = form.data.get('phone_number', '')
            email = form.data.get('email', '')
            
            # Prepare payment payload for PesaPal
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            payload = {
                "id": str(order.id),
                "currency": "USD",
                "amount": float(final_price),
                "description": f"Payment for order {order.id}",
                "callback_url": settings.PESAPAL_CALLBACK_URL,
                "notification_id": "16eef5c4-dc67-423c-8b44-dcd9cd412a17",
                "billing_address": {
                    "email_address": email,
                    "phone_number": phone_number,
                    "first_name": form.data.get('first_name', ''),
                    "middle_name": form.data.get('middle_name', ''),
                    "last_name": form.data.get('last_name', ''),
                    "line_1": form.data.get('street1', ''),
                }
            }
            print(str(payload))
            try:
                response = requests.post(settings.PESAPAL_CHECKOUT_URL, json=payload, headers=headers)
                response.raise_for_status()
                payment_response_data = response.json()
                print(str(payment_response_data))
                # Update payment status if the response was successful
                order.order_status = 'Pending'
                order.save()

                # Return the payment URL for the user to be redirected to PesaPal
                return JsonResponse({
                    'redirect_url': payment_response_data.get('redirect_url'),
                    'tracking_id': payment_response_data.get('order_tracking_id')
                }, status=200)

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': f'Payment initiation failed: {str(e)}'}, status=500)
        else:
            print("Form errors:", form.errors)
            return JsonResponse({'error': form.errors.as_json()}, status=400)



class PaymentStatus(APIView):
    def get(self, request, transaction_reference):
        try:
            payment = Payment.objects.get(transaction_reference=transaction_reference)
            query_url = f"https://www.pesapal.com/API/QueryPaymentDetails?transaction={payment.transaction_reference}&tracking={payment.tracking_id}"

            # Get a fresh access token
            token = get_access_token()
            if not token:
                return Response({'error': 'Failed to retrieve access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            headers = {
                'Authorization': f'Bearer {token}',
            }

            try:
                response = requests.get(query_url, headers=headers)
                response.raise_for_status()
                payment_status_data = response.json()

                return Response(payment_status_data, status=response.status_code)
            except requests.exceptions.RequestException as e:
                return Response({'error': f'Failed to query payment status: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

class IPNCallback(APIView):
    def post(self, request):
        tracking_id = request.data.get('OrderTrackingId')
        transaction_reference = request.data.get('OrderMerchantReference')
        status = request.data.get('status')

        try:
            payment = Payment.objects.get(transaction_reference=transaction_reference)
            payment.tracking_id = tracking_id
            payment.status = status
            payment.save()

            # Assuming status "COMPLETED" indicates a successful payment
            if status == "COMPLETED":
                user = payment.user  # Assuming your Payment model has a ForeignKey to the user
                order = Order.objects.get(id=payment.order_id)  # Fetch the associated order
                
                # Send confirmation email to the user and admin
                send_order_confirmation(user, settings.ADMIN_EMAIL)
                
                # Send order details to the user
                send_order_details(user, order)

            return Response({'message': 'Payment status updated'}, status=status.HTTP_200_OK)
        
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)


class SendConfirmationEmail:
    def send_order_confirmation_email(order):
        subject = 'Order Confirmation - Your Order with Sevaria'
        recipient = order.email  # Use the email associated with the order
        context = {
            'order': order,
            'order_items': order.items.all(),  # Assuming Order model has related items
        }
        # Render email content from a template
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = recipient

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)

def convert_currency(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))  # Extracting the data sent from frontend
        amount = data.get('amount')
        from_currency = data.get('fromCurrency')
        to_currency = data.get('toCurrency', 'USD')  # Default to USD if no target currency is specified

        # Log received data for debugging
        print(f"Received data: amount={amount}, from_currency={from_currency}, to_currency={to_currency}")

        # Define your Exchange Rate API key
        api_key = os.getenv('EXCHANGERATE_API')  # Ensure your API key is securely stored in environment variables
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"

        try:
            # Make the API request
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            data = response.json()

            # Check if the result is success and the target currency is available
            if data["result"] == "success" and to_currency in data["conversion_rates"]:
                conversion_rate = data["conversion_rates"][to_currency]
                print(conversion_rate)
                if conversion_rate is None:
                    return JsonResponse({'error': 'Conversion rate not available'}, status=400)

                try:
                    converted_amount = float(amount) * conversion_rate
                    return JsonResponse({'convertedAmount': converted_amount}, status=200)
                except ValueError:
                    return JsonResponse({'error': 'Invalid amount format'}, status=400)
            else:
                return JsonResponse({'error': 'Conversion failed or currency not supported'}, status=400)
            
        except requests.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

        except KeyError:
            return JsonResponse({'error': 'Currency data not available'}, status=500)
        





