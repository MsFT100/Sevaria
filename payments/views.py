import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from .models import Payment
from .serializers import PaymentSerializer
from payments.pesapalOath import get_access_token  # Assuming this file contains the get_access_token function

PESAPAL_CHECKOUT_URL = "https://www.pesapal.com/API/PostPesapalDirectOrderV4"

class InitiatePayment(APIView):
    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            # Save the payment with a unique transaction reference
            payment = serializer.save(transaction_reference="TRX-" + str(serializer.instance.id))

            # Get a fresh access token
            token = get_access_token()
            if not token:
                return Response({'error': 'Failed to retrieve access token.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Prepare the PesaPal request headers and payload
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            payload = {
                'Amount': payment.amount,
                'Description': f'Payment for order {payment.transaction_reference}',
                'Type': 'MERCHANT',
                'Reference': payment.transaction_reference,
                'PhoneNumber': payment.phone_number,
                'Email': request.data.get('email', 'example@example.com'),
            }

            # Send request to PesaPal
            try:
                response = requests.post(PESAPAL_CHECKOUT_URL, data=payload, headers=headers)
                response.raise_for_status()
                payment_response_data = response.json()

                # Handle successful response
                return Response(payment_response_data, status=status.HTTP_200_OK)
            except requests.exceptions.RequestException as e:
                return Response({'error': f'Payment initiation failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@csrf_exempt
@api_view(['POST'])
def pesapal_ipn(request):
    tracking_id = request.data.get('tracking_id')
    transaction_reference = request.data.get('transaction_reference')
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
