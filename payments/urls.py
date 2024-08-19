from django.urls import path
from . import views, pesapalOath

urlpatterns = [
    path('checkout-api/', views.CheckoutView.as_view(), name='checkout-api'),
    path('initiate/', views.InitiatePayment.as_view(), name='initiate_payment'),
    path('ipn/', views.IPNCallback.as_view(), name='pesapal_ipn'),
    path('oath/', pesapalOath.get_access_token, name='oath'),
]
