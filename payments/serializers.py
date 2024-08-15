from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'transaction_reference', 'phone_number', 'amount', 'status', 'tracking_id', 'date_created']
