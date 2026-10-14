from twilio.rest import Client
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class SMSService:
    def __init__(self):
        self.backend = settings.SMS_BACKEND
    
    def send_sms(self, phone_number, message):
        """Send SMS using configured backend"""
        if self.backend == 'twilio':
            return self._send_via_twilio(phone_number, message)
        elif self.backend == 'msg91':
            return self._send_via_msg91(phone_number, message)
        elif self.backend == 'fast2sms':
            return self._send_via_fast2sms(phone_number, message)
        else:
            logger.error(f"Unknown SMS backend: {self.backend}")
            return False
    
    def _send_via_twilio(self, phone_number, message):
        """Send SMS via Twilio"""
        try:
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            # Format phone number for Twilio (add +91 for Indian numbers)
            if not phone_number.startswith('+'):
                phone_number = '+91' + phone_number
            
            twilio_message = client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            
            logger.info(f"SMS sent via Twilio: {twilio_message.sid}")
            return True
        except Exception as e:
            logger.error(f"Twilio SMS error: {str(e)}")
            return False
    
    def _send_via_msg91(self, phone_number, message):
        """Send SMS via MSG91"""
        try:
            url = 'https://api.msg91.com/api/v5/flow/'
            headers = {
                'authkey': settings.MSG91_AUTH_KEY,
                'content-type': 'application/json'
            }
            
            payload = {
                'sender': settings.MSG91_SENDER_ID,
                'route': settings.MSG91_ROUTE,
                'country': '91',
                'sms': [{
                    'message': message,
                    'to': [phone_number]
                }]
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"SMS sent via MSG91 to {phone_number}")
                return True
            else:
                logger.error(f"MSG91 SMS error: {response.text}")
                return False
        except Exception as e:
            logger.error(f"MSG91 SMS error: {str(e)}")
            return False
    
    def _send_via_fast2sms(self, phone_number, message):
        """Send SMS via Fast2SMS"""
        try:
            url = 'https://www.fast2sms.com/dev/bulkV2'
            headers = {
                'authorization': settings.FAST2SMS_API_KEY,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'route': 'dlt',
                'sender_id': 'BharatKart',
                'message': message,
                'language': 'english',
                'flash': 0,
                'numbers': phone_number
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('return'):
                    logger.info(f"SMS sent via Fast2SMS to {phone_number}")
                    return True
            
            logger.error(f"Fast2SMS error: {response.text}")
            return False
        except Exception as e:
            logger.error(f"Fast2SMS error: {str(e)}")
            return False


class SMSNotifications:
    """Predefined SMS templates"""
    
    def __init__(self):
        self.sms_service = SMSService()
    
    def send_order_confirmation(self, order):
        """Send order confirmation SMS"""
        message = (
            f"Dear {order.user.first_name},\n"
            f"Your order {order.order_number} has been confirmed.\n"
            f"Total: Rs. {order.total}\n"
            f"Track your order: {settings.SITE_URL}/orders/{order.id}/\n"
            f"Thank you for shopping with BharatKart!"
        )
        return self.sms_service.send_sms(str(order.user.phone), message)
    
    def send_order_shipped(self, order):
        """Send order shipped SMS"""
        message = (
            f"Good news! Your order {order.order_number} has been shipped.\n"
            f"Tracking ID: {order.tracking_number}\n"
            f"Courier: {order.courier_name}\n"
            f"Track: {settings.SITE_URL}/orders/{order.id}/"
        )
        return self.sms_service.send_sms(str(order.user.phone), message)
    
    def send_order_delivered(self, order):
        """Send order delivered SMS"""
        message = (
            f"Your order {order.order_number} has been delivered.\n"
            f"Please rate your experience.\n"
            f"Feedback: {settings.SITE_URL}/orders/{order.id}/rate/"
        )
        return self.sms_service.send_sms(str(order.user.phone), message)
    
    def send_otp(self, phone_number, otp):
        """Send OTP for verification"""
        message = f"Your OTP for BharatKart is: {otp}. Valid for 10 minutes."
        return self.sms_service.send_sms(phone_number, message)
    
    def send_payment_confirmation(self, order):
        """Send payment confirmation SMS"""
        message = (
            f"Payment received for order {order.order_number}.\n"
            f"Amount: Rs. {order.total}\n"
            f"Payment method: {order.payment_method}"
        )
        return self.sms_service.send_sms(str(order.user.phone), message)
    
    def send_refund_initiated(self, order, amount):
        """Send refund initiated SMS"""
        message = (
            f"Refund of Rs. {amount} has been initiated for order {order.order_number}.\n"
            f"The amount will be credited to your account within 5-7 business days."
        )
        return self.sms_service.send_sms(str(order.user.phone), message)
    
    def send_chat_notification(self, user, room):
        """Send chat notification SMS"""
        message = (
            f"You have a new message in your BharatKart support chat.\n"
            f"Subject: {room.subject}\n"
            f"View: {settings.SITE_URL}/chat/{room.id}/"
        )
        return self.sms_service.send_sms(str(user.phone), message)