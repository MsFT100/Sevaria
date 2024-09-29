from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.generic import DetailView
from .models import Product, Order, OrderItem, ProductVariant


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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# Custom OrderDetailView for detailed admin view
class OrderDetailView(DetailView):
    model = Order
    template_name = "admin/order_detail.html"
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.all()
        
        return context



# Register Order with custom detail view and inlines
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'formatted_usd_amount', 'order_status','payment_status','shipping_amount', 'detail']
    inlines = [OrderItemInline]

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
    
    def formatted_usd_amount(self, obj):
        return f'USD {obj.total_price:.2f}'
    formatted_usd_amount.short_description = 'USD Amount'

    def formatted_local_amount(self, obj):
        return f'K {obj.shipping_amount:.2f}'
    formatted_local_amount.short_description = 'Local Amount'
