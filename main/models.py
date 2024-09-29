from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Product(models.Model):

    CATEGORY = [
        ('DRESS', 'Dress'),
        ('BAGS', 'Bags'),
        ('T-Shirts', 'T-Shirts'),
        ('SHIRTS', 'Shirts'),
        ('SKIRTS', 'Skirts'),
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
        ('WHITE', 'White'),
        ('LIGHT BLUE', 'Light blue'),
        ('DARK BLUE', 'Dark blue'),
        ('BROWN', 'Brown'),
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

    TRANSACTION_STATUSES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    # Order Details
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    first_name = models.TextField(max_length=255, blank=True, default='nill')
    last_name = models.TextField(max_length=255, blank=True, default='nill')
    email = models.EmailField(default='nill')
    street = models.CharField(max_length=255, blank=True, default='nill')
    city = models.CharField(max_length=255, blank=True, default='nill')
    state = models.CharField(max_length=255, blank=True, default='nill')
    zip_code = models.CharField(max_length=255, blank=True, default='nill')
    country = models.CharField(max_length=255, blank=True, default='nill')
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    # Payment Details
    transaction_reference = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_status = models.CharField(max_length=20, choices=TRANSACTION_STATUSES, default='PENDING')
    tracking_id = models.CharField(max_length=255, null=True, blank=True)  # From Payment model
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # Optional for payments

    # Shipping Details
    shipping_provider = models.CharField(max_length=255, blank=True, null=True)
    shipping_token = models.CharField(max_length=255, blank=True, null=True)
    shipping_terms = models.TextField(blank=True, null=True)
    shipping_provider_image = models.URLField(blank=True, null=True)
    shipping_currency = models.CharField(max_length=10, blank=True, null=True)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    


    
    def __str__(self):
        return f'Order {self.id} by {self.user.username if self.user else "Guest"}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'


    




    






