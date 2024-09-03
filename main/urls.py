from django.urls import path
from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('shop/', views.Shop.as_view(), name='shop'),
    path('bags/', views.Bags.as_view(), name='Bags'),
    path('about/', views.About.as_view(), name='about'),
    
    path('product/<int:pk>/', views.ProductDetail.as_view(), name='product_detail'),
    path('add-to-cart/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('get-cart-items/', views.cart_view, name='get-cart-items'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.CheckOut.as_view(), name='checkout'),
    
    path('paymentresult/', views.SuccessPage.as_view(), name='pay_status'),

    path('adminlogin/', views.AdminLogin.as_view(), name='admin_login'),
    path('admin/dashboard/', views.AdminDashboard.as_view(), name='admin_dashboard'),
]
