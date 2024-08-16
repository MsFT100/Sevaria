from django.forms import ModelForm
from .models import Payment

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['phone_number', 'amount', 'email', 'country', 'first_name', 'last_name']
        