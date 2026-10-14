from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from apps.notifications.sms_service import SMSNotifications
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_order_confirmation_sms(order_id):
    """Send order confirmation SMS"""
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        sms_service = SMSNotifications()
        sms_service.send_order_confirmation(order)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")

@shared_task
def send_order_shipped_sms(order_id):
    """Send order shipped SMS"""
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        sms_service = SMSNotifications()
        sms_service.send_order_shipped(order)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")

@shared_task
def send_payment_confirmation_sms(order_id):
    """Send payment confirmation SMS"""
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id)
        sms_service = SMSNotifications()
        sms_service.send_payment_confirmation(order)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found")