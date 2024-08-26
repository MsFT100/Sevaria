from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Product(models.Model):

    CATEGORY = [
        ('DRESS', 'Dress'),
        ('BAGS', 'Bags'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField(default='null')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY, default='DRESS')
    image = models.ImageField(upload_to='product_images/')
    alternate_image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    SIZES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    COLORS = [
        ('RED', 'Red'),
        ('BLUE', 'Blue'),
        ('GREEN', 'Green'),
        ('BLACK', 'Black'),
    ]

    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=2, choices=SIZES)
    color = models.CharField(max_length=10, choices=COLORS)
    stock = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tracking_id = models.CharField(max_length=255, null=True, blank=True)
    order_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'

class ShippingInfo(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    tracking_number = models.CharField(max_length=50, blank=True, null=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f'Shipping info for Order {self.order.id}'
    

class Cart(models.Model):
    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Cart {self.id} for {self.user.username}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'
    






