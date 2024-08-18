from django.shortcuts import get_object_or_404, render
from django.views import View

from main.models import Product

# Create your views here.
class Index( View):
    def get(self, request):
        
        return render(request, 'pages/index.html')
    

class CheckOut(View):
    def get(self, request):
        return render(request, 'pages/checkout.html')

class CheckOutPage(View):
    def get(self, request):
        return render(request, 'pages/successfulpay.html')
    

class Shop(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'pages/shop.html', {'products': products})

class Productdetail(View):
    def get(request, product_id):
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'ecommerce/product_detail.html', {'product': product})


class AdminLogin(View):
    def get(self, request):
        return render(request, 'admin/login.html')
class AdminDashboard(View):
    def get(self, request):
        return render(request, 'admin/dashboard.html')
def custom_404_view(request, exception=None):
    return render(request, 'navigation/404.html', status=404)