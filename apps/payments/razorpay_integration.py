import razorpay
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
import hmac
import hashlib
import json

class RazorpayPayment:
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, receipt_id, notes=None):
        """Create Razorpay order"""
        try:
            order_data = {
                'amount': int(amount * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': receipt_id,
                'payment_capture': 1,  # Auto capture
            }
            
            if notes:
                order_data['notes'] = notes
            
            order = self.client.order.create(data=order_data)
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key': settings.RAZORPAY_KEY_ID,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify Razorpay payment signature"""
        try:
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return {'success': True}
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_webhook_signature(self, webhook_body, webhook_signature):
        """Verify webhook signature"""
        try:
            expected_signature = hmac.new(
                settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8'),
                webhook_body.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(expected_signature, webhook_signature)
        except Exception:
            return False
    
    def capture_payment(self, payment_id, amount=None):
        """Capture payment"""
        try:
            if amount:
                capture_data = {'amount': int(amount * 100)}
            else:
                capture_data = {}
            
            payment = self.client.payment.capture(payment_id, capture_data)
            return {
                'success': True,
                'payment': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def refund_payment(self, payment_id, amount=None):
        """Refund payment"""
        try:
            if amount:
                refund_data = {'amount': int(amount * 100)}
            else:
                refund_data = {}
            
            refund = self.client.payment.refund(payment_id, refund_data)
            return {
                'success': True,
                'refund': refund
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_payment_details(self, payment_id):
        """Get payment details"""
        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'success': True,
                'payment': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Payment Views
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.orders.models import Order
from .models import Payment

@login_required
def create_razorpay_order(request, order_id):
    """Create Razorpay order for payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return JsonResponse({'error': 'Order already paid'}, status=400)
    
    razorpay = RazorpayPayment()
    result = razorpay.create_order(
        amount=float(order.total),
        receipt_id=order.order_number,
        notes={
            'order_id': order.id,
            'user_id': request.user.id,
            'user_email': request.user.email,
        }
    )
    
    if result['success']:
        # Save payment record
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total,
            method='razorpay',
            status='pending',
            gateway='razorpay',
            transaction_id=result['order_id'],
        )
        
        return JsonResponse({
            'success': True,
            'key': settings.RAZORPAY_KEY_ID,
            'order_id': result['order_id'],
            'amount': result['amount'],
            'currency': result['currency'],
            'payment_id': payment.id,
            'name': 'BharatKart',
            'description': f'Payment for order {order.order_number}',
            'prefill': {
                'name': f'{request.user.first_name} {request.user.last_name}',
                'email': request.user.email,
                'contact': str(request.user.phone) if request.user.phone else '',
            },
            'theme': {
                'color': '#0d6efd'
            }
        })
    
    return JsonResponse({'error': result['error']}, status=400)

@csrf_exempt
@require_POST
def razorpay_webhook(request):
    """Handle Razorpay webhook"""
    webhook_body = request.body.decode('utf-8')
    webhook_signature = request.headers.get('X-Razorpay-Signature', '')
    
    razorpay = RazorpayPayment()
    
    if not razorpay.verify_webhook_signature(webhook_body, webhook_signature):
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    event = json.loads(webhook_body)
    event_type = event.get('event')
    
    if event_type == 'payment.captured':
        payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
        order_id = payment_data.get('order_id')
        payment_id = payment_data.get('id')
        
        try:
            payment = Payment.objects.get(transaction_id=order_id)
            payment.status = 'completed'
            payment.transaction_id = payment_id
            payment.gateway_response = event
            payment.save()
            
            # Update order
            order = payment.order
            order.payment_status = 'paid'
            order.payment_method = 'razorpay'
            order.payment_id = payment_id
            order.save()
            
            # Send confirmation
            from apps.orders.tasks import send_order_confirmation
            send_order_confirmation.delay(order.id)
            
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
    
    elif event_type == 'payment.failed':
        payment_data = event.get('payload', {}).get('payment', {}).get('entity', {})
        order_id = payment_data.get('order_id')
        
        try:
            payment = Payment.objects.get(transaction_id=order_id)
            payment.status = 'failed'
            payment.failure_reason = payment_data.get('error_description', '')
            payment.gateway_response = event
            payment.save()
            
            # Update order
            order = payment.order
            order.payment_status = 'failed'
            order.save()
            
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)
    
    return JsonResponse({'status': 'success'})