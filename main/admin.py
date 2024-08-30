from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.generic import DetailView
from .models import Product, Order, OrderItem, ProductVariant, ShippingInfo


# Register Product with basic admin configuration
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]
    list_display = ['name', 'price']

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'size', 'color', 'stock']


# Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# Inline for Shipping Info
class ShippingInfoInline(admin.StackedInline):
    model = ShippingInfo
    extra = 0
    readonly_fields = ['tracking_number', 'carrier', 'estimated_delivery_date']


# Custom OrderDetailView for detailed admin view
class OrderDetailView(DetailView):
    model = Order
    template_name = "admin/order_detail.html"
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Use the 'items' related name to access OrderItems
        context['order_items'] = self.object.items.all()  # Use the related name 'items' directly
        # Add shipping info if available
        context['shipping_info'] = ShippingInfo.objects.filter(order=self.object).first()
        return context



# Register Order with custom detail view and inlines
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'total_price', 'order_status', 'detail']
    inlines = [OrderItemInline, ShippingInfoInline]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<pk>/detail/",
                self.admin_site.admin_view(OrderDetailView.as_view()),
                name="products_order_detail",
            ),
        ]
        return custom_urls + urls

    def detail(self, obj: Order) -> str:
        url = reverse("admin:products_order_detail", args=[obj.pk])
        return format_html(f'<a href="{url}">📝 View Details</a>')
