from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView

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

class ProductDetail(DetailView):
    model = Product
    template_name = 'pages/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        product_id = self.kwargs.get('product_id')
        return super().get_object(queryset)  

class AdminLogin(View):
    def get(self, request):
        return render(request, 'admin/login.html')
class AdminDashboard(View):
    def get(self, request):
        return render(request, 'admin/dashboard.html')
def custom_404_view(request, exception=None):
    return render(request, 'navigation/404.html', status=404)