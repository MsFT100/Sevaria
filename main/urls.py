from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('shop/', views.Shop.as_view(), name='shop'),
    path('checkout/', views.CheckOut.as_view(), name='checkout'),
]
