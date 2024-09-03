from django.conf import settings
from django.core.mail import send_mail

from django.conf import settings
from django.core.mail import send_mail

def send_email(subject, message, recipient_list):
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, recipient_list)

def send_order_confirmation(user, admin_email):
    # Email to the user
    subject_user = 'Order Confirmation - Thank you for your purchase!'
    message_user = f'Hi {user.username}, your order has been placed successfully. Thank you for shopping with us!'
    recipient_user = [user.email]
    send_email(subject_user, message_user, recipient_user)

    # Email to the admin
    subject_admin = 'New Order Placed'
    message_admin = f'A new order has been placed by {user.username}. Please review the order details in the admin panel.'
    recipient_admin = [admin_email]
    send_email(subject_admin, message_admin)

def send_order_details(user, order):
    # Send order details to the user
    subject = 'Your Order Details'
    message = f'Hi {user.username}, here are the details of your order:\n\n{order.details}'
    recipient_list = [user.email]
    send_email(subject, message, recipient_list)
