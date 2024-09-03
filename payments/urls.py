from django.urls import path
from . import views, pesapalOath

urlpatterns = [
    path('get-shipping-rates/', views.GetShippingRatesView.as_view(), name='get_shipping_rates'),
    path('checkout-api/', views.CheckoutView.as_view(), name='checkout-api'),
    path('ipn/', views.IPNCallback.as_view(), name='pesapal_ipn'),
    path('oath/', pesapalOath.get_access_token, name='oath'),
    path('convert-currency/', views.convert_currency, name='convertcurrency'),
]
