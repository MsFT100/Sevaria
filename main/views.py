from django.shortcuts import render
from django.views import View

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
        return render(request, 'pages/shop.html')
    

def custom_404_view(request, exception=None):
    return render(request, 'navigation/404.html', status=404)