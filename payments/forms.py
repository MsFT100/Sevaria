from django.forms import ModelForm
from main.models import Order

class CheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'total_price']
        