# utils.py


from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f"Order Confirmation - {order.transaction_reference}"
    message = f"""
    Dear {order.first_name},

    Thank you for your order! Your order number is {order.id}.
    Shipping to: {order.shipping_address}
    Tracking number: {order.tracking_number}

    You can track your order here: [Tracking Link]

    Regards,
    Your Company Name
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [order.user.email],
        fail_silently=False,
    )

def send_admin_notification_email(order):
    subject = f"New Order - {order.order_number}"
    message = f"""
    A new order has been placed.

    Order Number: {order.order_number}
    Customer: {order.user.username}
    Shipping Address: {order.shipping_address}
    Tracking Number: {order.tracking_number}

    Please prepare the order for shipment.

    Regards,
    Your Company Name
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
        fail_silently=False,
    )
