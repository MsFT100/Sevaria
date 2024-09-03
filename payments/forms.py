from django.forms import ModelForm
from main.models import Order

class CheckoutForm(ModelForm):
    class Meta:
        model = Order
        fields = [ 'first_name', 'last_name', 'email', 'street', 'city', 'state', 'country', 'zip_code', 'total_price']
        
class ShippingForm(ModelForm):
    class Meta:
        model = Order
        fields = [ 'first_name', 'last_name', 'email', 'street', 'city', 'state', 'country', 'zip_code', 'total_price']
        