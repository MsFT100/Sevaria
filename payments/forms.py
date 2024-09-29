from django.forms import ModelForm
from main.models import Order

class CheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = [ 'first_name', 'last_name', 'email', 'street', 'city', 'state', 'country', 'zip_code', 'total_price', 'shipping_provider', 'shipping_token', 'shipping_terms', 'shipping_provider_image', 'shipping_currency', 'shipping_amount']
        
class ShippingForm(ModelForm):
    class Meta:
        model = Order
        fields = [ 'first_name', 'last_name', 'email', 'street', 'city', 'state', 'country', 'zip_code', 'total_price']
        