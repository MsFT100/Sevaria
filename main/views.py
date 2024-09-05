import json
from django.conf import settings
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from django.views.generic import DetailView
from django.db.models import Q
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from main.models import Order, Product, ProductVariant

# Create your views here.
class Index( View):
    def get(self, request):
        
        return render(request, 'pages/index.html')
    
class Error( View):
    def get(self, request):
        
        return render(request, 'error.html')
class CheckOut(View):
    def get(self, request):
        return render(request, 'pages/checkout.html')

class SuccessPage(View):
    def get(self, request):
        # Extract parameters from URL
        tracking_id = request.GET.get('OrderTrackingId')
        merchant_reference = request.GET.get('OrderMerchantReference')

        print(tracking_id)
        # Validate the parameters
        if not tracking_id or not merchant_reference:
            return render(request, 'error.html', {'message': 'Missing parameters'})

        # Query the database for the order
        order = get_object_or_404(Order, transaction_reference=tracking_id)
        #clear the cart
        clear_cart()

        #send the email
        order.payment_status = 'Completed'
        order.tracking_id = tracking_id
        order.save()
        
        send_order_confirmation_email(self,order)
        send_admin_order_confirmation_email(self,order)
        # Pass order details to the template
        context = {
            'order': order,
        }
        
        return render(request, 'pages/successfulpay.html', context)
    

class Shop(View):
    def get(self, request):
        products = Product.objects.filter(Q(category='Dress') | Q(category='Shirt') | Q(category='Skirt') | Q(category='T-Shirts'))
        return render(request, 'pages/shop.html', {'products': products})

class Bags(View):
    def get(self, request):
        products = Product.objects.filter(category='Bags')
        return render(request, 'pages/bags.html', {'products': products})
    
class ProductDetail(DetailView):
    model = Product
    template_name = 'pages/product_detail.html'
    context_object_name = 'product'

    def get_object(self, queryset=None):
        product_id = self.kwargs.get('product_id')
        return super().get_object(queryset)  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        # Retrieve variants of the product
        variants = ProductVariant.objects.filter(product=product)

         # Create a dictionary for stock information based on size and color
        stock_info = {}
        colors = set()
        sizes = set()

        for variant in variants:
            key = f"{variant.size}-{variant.color}"
            stock_info[key] = variant.stock
            colors.add(variant.color)
            sizes.add(variant.size)

        context['colors'] = sorted(colors)
        context['sizes'] = sorted(sizes)
        context['stock_info'] = stock_info  # Pass stock info to the template
        context['variants'] = variants  # Pass the variants to the template # Pass the variants to the template
        
        return context


class About(View):
    def get(self, request):
        return render(request, 'pages/about.html')
    

class AdminLogin(View):
    def get(self, request):
        return render(request, 'admin/login.html')
class AdminDashboard(View):
    def get(self, request):
        return render(request, 'admin/dashboard.html')
def custom_404_view(request, exception=None):
    return render(request, 'navigation/404.html', status=404)


class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            size = data.get('size')
            color = data.get('color')
            quantity = int(data.get('quantity', 1))

            # Get the product and variant
            product = get_object_or_404(Product, id=product_id)
            variant = get_object_or_404(ProductVariant, product=product, size=size, color=color)

            # Check stock availability
            if quantity > variant.stock:
                return JsonResponse({'error': 'Not enough stock'}, status=400)

            # Example of saving to session-based cart
            cart = request.session.get('cart', {})
            item_key = f"{product_id}_{size}_{color}"

            if item_key in cart:
                cart[item_key]['quantity'] += quantity
            else:
                cart[item_key] = {
                    'product_id': product_id,
                    'size': size,
                    'color': color,
                    'quantity': quantity,
                }

            request.session['cart'] = cart

            return JsonResponse({'success': True, 'cart': cart})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['POST'])


def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []

    for item in cart.values():
        # Get the product based on the product_id in the cart
        product = get_object_or_404(Product, id=item['product_id'])
        
        # Append the product details along with the cart item data
        cart_items.append({
            'name': product.name,
            'price': str(product.price),
            'quantity': item['quantity'],
            'size': item['size'],
            'color': item['color'],
            'image_url': product.image.url if product.image else '/static/default-image.jpg'
        })

    return JsonResponse({'cart': cart_items})

def clear_cart(request):
    if request.method == 'POST':
        request.session['cart'] = {}
        return JsonResponse({'success': True, 'message': 'Cart has been cleared.'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def send_order_confirmation_email(self, order):
        subject = 'Order Confirmation - Your Order with Sevaria'
        recipient = order.email  # Use the email associated with the order
        context = {
            'order': order,
            'order_items': order.items.all(),  # Assuming Order model has related items
        }
        # Render email content from a template
        html_message = render_to_string('emails/order_confirmation.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = recipient

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def send_admin_order_confirmation_email(self, order):
        subject = 'An order has been placed'

        recipient = 'sevariastudios@gmail.com'  # Use the email associated with the order
        context = {
            'order': order,
            'order_items': order.items.all(),  # Assuming Order model has related items
        }
        # Render email content from a template
        html_message = render_to_string('emails/admin_success_confirmation.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = recipient

        send_mail(subject, plain_message, from_email, [to], html_message=html_message)