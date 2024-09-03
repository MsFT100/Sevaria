# utils.py
def send_order_confirmation_email(order):
    subject = f"Order Confirmation - {order.order_number}"
    message = f"""
    Dear {order.user.username},

    Thank you for your order! Your order number is {order.order_number}.
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
