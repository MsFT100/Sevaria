from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
import requests
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from rest_framework.views import APIView
from .models import Payment
from main.models import Cart, OrderItem, Order, Product, ProductVariant
from .forms import CheckoutForm

from payments.pesapalOath import get_access_token  # Assuming this file contains the get_access_token function


class CheckoutView(View):
    def get(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        
        
        
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
            
            # Iterate through the cart items
            for item_key, item in cart.items():
                product = Product.objects.get(id=item['product_id'])
                
                

                # Calculate the total price for the item
                item_total_price = product.price * item['quantity']
                total_price += item_total_price
                
                print(total_price)
                # Create OrderItem for each cart item
                OrderItem.objects.create(
                    order=order,  # Use the saved order instance
                    product=product,
                    quantity=item['quantity']  # Retrieve quantity from session data
                )
            
            # Set the total price for the order
            order.total_price = total_price
            order.save()  # Save the updated order with total_price

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
                "amount": float(order.total_price),
                "description": f"Payment for order {order.id}",
                "callback_url": settings.PESAPAL_CALLBACK_URL,
                "notification_id": "16eef5c4-dc67-423c-8b44-dcd9cd412a17",
                "billing_address": {
                    "email_address": email,
                    "phone_number": phone_number,
                    "first_name": form.data.get('first_name', ''),
                    "middle_name": form.data.get('middle_name', ''),
                    "last_name": form.data.get('last_name', ''),
                    "line_1": form.cleaned_data['shipping_address'],
                }
            }
            #print(str(payload))
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


class InitiatePayment(View):
    def post(self, request):
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Create a new payment instance
            
            payment = form.save()

            # Get a fresh access token
            token = get_access_token()
            if not token:
                return JsonResponse({'error': 'Failed to retrieve access token.'}, status=500)

            # Prepare the PesaPal request headers and payload
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            # Extract data from the form
            phone_number = form.data.get('phone_number', '')
            email = form.data.get('email', '')

            payload = {
                "id": str(payment.transaction_reference),
                "currency": "KES",  # Adjust currency code as per your requirement
                "amount": float(format(payment.amount, '.2f')),
                "description": f"Payment for order {str(payment.transaction_reference)}",
                "callback_url": settings.PESAPAL_CALLBACK_URL,  # Ensure this is set correctly in settings
                "notification_id": settings.IPN_ID,  # Replace with your notification ID
                "billing_address": {
                    "email_address": email ,
                    "phone_number": phone_number,
                    "country_code": "KE",  # Adjust as needed
                    "first_name": form.data.get('first_name', ''),
                    "middle_name": form.data.get('middle_name', ''),
                    "last_name": form.data.get('last_name', ''),
                    "line_1": form.data.get('line_1', ''),
                    "line_2": form.data.get('line_2', ''),
                    "city": form.data.get('city', ''),
                    "state": form.data.get('state', ''),
                    "postal_code": form.data.get('postal_code', ''),
                    "zip_code": form.data.get('zip_code', '')
                }
            }
            #print(str(payload))
            # Send request to PesaPal
            try:
                response = requests.post(settings.PESAPAL_CHECKOUT_URL, json=payload, headers=headers)
                response.raise_for_status()
                payment_response_data = response.json()

                # Update payment status if the response was successful
                payment.status = 'pending'
                payment.save()
                print(str(payment_response_data))
                # Return the payment URL for the user to be redirected to PesaPal
                return JsonResponse({
                    'redirect_url': payment_response_data.get('redirect_url'),
                    'tracking_id': payment_response_data.get('order_tracking_id')
                }, status=200)

            except requests.exceptions.RequestException as e:
                return JsonResponse({'error': f'Payment initiation failed: {str(e)}'}, status=500)
        
        return JsonResponse({'errors': form.errors}, status=400)

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

            return Response({'message': 'Payment status updated'}, status=status.HTTP_200_OK)
        
        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)

# Helper function to refresh OAuth token
def getOath():
    token = get_access_token()
    if token:
        print(f"Access Token: {token}")
    else:
        print("Failed to retrieve access token.")
