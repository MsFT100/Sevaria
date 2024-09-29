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

from main.views import clear_cart
from payments.send_email import send_order_confirmation, send_order_details
from payments.shipshap import get_shipping_rates

from main.models import OrderItem, Order, Product, ProductVariant
from .forms import CheckoutForm, ShippingForm

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
            cart = request.session.get('cart', {})
            
            # Debugging output to check cart data
            print("Cart data received:", cart)

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

                # Ensure total_price is a valid number
                try:
                    total_price = float(total_price)
                except ValueError:
                    return JsonResponse({"error": "Invalid total price"}, status=400)

                # Initialize total_weight
                total_weight = 0

                # Calculate total weight assuming each product has a weight of 1kg
                try:
                    for item_key, item in cart.items():
                        print(item)
                        total_weight += item.get('quantity', 0)
                except (TypeError, KeyError) as e:
                    print(f"Error accessing cart items: {e}")
                    return JsonResponse({"error": "Invalid cart items"}, status=400)

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
                        "non_delivery_option": "return",
                        "certify_signer": "Sevaria",
                        "certify": True,
                        "contents_explanation": "clothing items",
                        "items": [
                            {
                                "weight_unit": "kg",
                                "value_currency": "USD",
                                "description": "clothes",
                                "quantity": total_weight,  # Total quantity of items
                                "net_weight": str(total_weight),  # Assuming 1kg per item
                                "value_amount": total_price,
                                "origin_country": "KE",
                                "is_test": True
                            }
                        ],
                        "incoterm": "DDP",
                        "eel_pfc": "NOEEI 30.37(a)",
                        "is_test": True
                    },
                    "parcels": [
                        {
                            "weight_unit": "kg",
                            "length": "44",
                            "width": "33",
                            "height": "5",
                            "length_unit": "cm",
                            "weight": str(total_weight),  # Total weight of all items
                            "is_test": True
                        }
                    ],
                    "is_test": True
                }

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
                    return JsonResponse({"rates": rates})
                except requests.exceptions.RequestException as e:
                    print(f"Request failed: {e}")
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
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            else:
                order.user = None  # Guest checkout

            cart = request.session.get('cart', {})
            total_price = form.cleaned_data.get('total_price', 0)
            
            
            #print("Cart data:", cart)

         
            # Populate shipping details
            
            shipping_provider = form.cleaned_data.get('shipping_provider', '')
            shipping_token = form.cleaned_data.get('shipping_token', '')
            shipping_terms = form.cleaned_data.get('shipping_terms', '')
            shipping_provider_image = form.cleaned_data.get('shipping_provider_image', '')
            shipping_currency = form.cleaned_data.get('shipping_currency', '')
            shipping_amount = form.cleaned_data.get('shipping_amount', 0)
            shipping_amount_local = form.cleaned_data.get('shipping_amount_local', 0)
            

            
            order.shipping_provider = shipping_provider
            order.shipping_token = shipping_token
            order.shipping_terms = shipping_terms
            order.shipping_provider_image = shipping_provider_image
            order.shipping_currency = shipping_currency
            #skip amount as we want it in usd
            
            

            #print("Shipping amount is = ", shipping_amount)
            #print("Shipping shipping_provider is = ", shipping_provider)
            #print("Shipping shipping_token = ", shipping_token)
            #print("Shipping shipping_terms = ", shipping_terms)
            #print("Shipping shipping_provider_image = ", shipping_provider_image)
            #print("Shipping shipping_amount_local = ", shipping_amount_local)
            #print("Shipping shipping_estimated_days = ", shipping_terms)

            # Save the order first
            order.save()
            # Iterate through the cart items
            for item_key, item in cart.items():
                product = Product.objects.get(id=item['product_id'])
                
                # do some calculations
                item_total_price = product.price * item['quantity']
                print(total_price)
                get_usd = total_price - item_total_price
                print('ship price', item_total_price)
                print("Shipping price", get_usd)

                order.shipping_amount = get_usd
                # Create OrderItem for each cart item
                OrderItem.objects.create(
                    order=order,  # Use the saved order instance
                    product=product,
                    quantity=item['quantity']  # Retrieve quantity from session data
                )

            order.total_price = total_price
            order.save()
            

            token = get_access_token()
            #print(token)
            if not token:
                return JsonResponse({'error': 'Failed to retrieve access token.'}, status=500)

            phone_number = form.cleaned_data.get('phone_number', '')
            email = form.cleaned_data.get('email', '')
            payload = {
                "id": str(order.id),
                "currency": "USD",
                "amount": float(total_price),
                "description": f"Payment for order {order.id}",
                "callback_url": settings.PESAPAL_CALLBACK_URL,
                "notification_id": "16eef5c4-dc67-423c-8b44-dcd9cd412a17",
                "billing_address": {
                    "email_address": email,
                    "phone_number": phone_number,
                    "first_name": form.cleaned_data.get('first_name', ''),
                    "middle_name": form.cleaned_data.get('middle_name', ''),
                    "last_name": form.cleaned_data.get('last_name', ''),
                    "line_1": form.cleaned_data.get('street1', ''),
                }
            }

            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            try:
                response = requests.post(settings.PESAPAL_CHECKOUT_URL, json=payload, headers=headers)
                response.raise_for_status()
                payment_response_data = response.json()

                order.transaction_reference = payment_response_data.get('order_tracking_id')
                order.payment_status = 'PENDING'  # Update this based on actual payment response
                order.save()

                return JsonResponse({
                    'redirect_url': payment_response_data.get('redirect_url'),
                    'tracking_id': order.transaction_reference
                }, status=200)

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': f'Payment initiation failed: {str(e)}'}, status=500)
        else:
            return JsonResponse({'error': form.errors.as_json()}, status=400)



class PaymentStatus(APIView):
    def get(self, request, transaction_reference):
        order = get_object_or_404(Order, transaction_reference=transaction_reference)
        tracking_id = order.tracking_id
        query_url = f"https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={tracking_id}"

        token = get_access_token()
        if not token:
            return Response({'error': 'Failed to retrieve access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(query_url, headers=headers)
            response.raise_for_status()
            payment_status_data = response.json()
            order.payment_status = payment_status_data.get('payment_status_description', 'FAILED')
            order.save()

            return Response(payment_status_data, status=response.status_code)
        except requests.exceptions.RequestException as e:
            return Response({'error': f'Failed to query payment status: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class IPNCallback(APIView):
    def post(self, request):
        tracking_id = request.data.get('OrderTrackingId')
        transaction_reference = request.data.get('OrderMerchantReference')

        # Get transaction status from Pesapal
        query_url = f"https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={tracking_id}"
        token = get_access_token()
        if not token:
            return Response({'error': 'Failed to retrieve access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.get(query_url, headers=headers)
            response.raise_for_status()
            payment_status_data = response.json()
            status_description = payment_status_data.get('payment_status_description', 'FAILED')

            print(payment_status_data)
            # Update order with the new status and details
            try:
                order = Order.objects.get(transaction_reference=transaction_reference)
                order.tracking_id = tracking_id
                order.payment_status = status_description
                order.save()

                # Additional actions based on status
                clear_cart()
                if status_description == "COMPLETED":
                    send_order_confirmation_email(order)

                # Respond back to Pesapal
                ipn_response = {
                    "orderNotificationType": "IPNCHANGE",
                    "orderTrackingId": tracking_id,
                    "orderMerchantReference": transaction_reference,
                    "status": 200  # Confirm receipt
                }
                return Response(ipn_response, status=status.HTTP_200_OK)

            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        except requests.exceptions.RequestException as e:
            return Response({'error': f'Failed to get transaction status: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        #print(f"Received data: amount={amount}, from_currency={from_currency}, to_currency={to_currency}")

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
        





