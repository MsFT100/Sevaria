from django.shortcuts import render
from django.views import View

# Create your views here.
class Index( View):
    def get(self, request):
        
        return render(request, 'pages/index.html')
    

class CheckOut(View):
    def get(self, request):
        return render(request, 'pages/checkout.html')
    
class Shop(View):
    def get(self, request):
        return render(request, 'pages/shop.html')
