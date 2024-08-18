from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('shop/', views.Shop.as_view(), name='shop'),
    path('product/<int:product_id>/', views.ProductDetail.as_view(), name='product_detail'),
    path('checkout/', views.CheckOut.as_view(), name='checkout'),
    path('paymentresult/', views.CheckOutPage.as_view(), name='pay_status'),

    path('adminlogin/', views.AdminLogin.as_view(), name='admin_login'),
    path('admin/dashboard/', views.AdminDashboard.as_view(), name='admin_dashboard'),
]
