import hashlib
import base64
import json
import requests
from django.conf import settings
from django.http import JsonResponse
import uuid

class PhonePePayment:
    def __init__(self):
        self.merchant_id = settings.PHONEPE_MERCHANT_ID
        self.salt_key = settings.PHONEPE_SALT_KEY
        self.salt_index = settings.PHONEPE_SALT_INDEX
        self.env = settings.PHONEPE_ENV
        self.callback_url = settings.PHONEPE_CALLBACK_URL
        
        if self.env == 'production':
            self.base_url = 'https://api.phonepe.com/apis/hermes'
            self.payment_url = 'https://mercury.phonepe.com/transact'
        else:
            self.base_url = 'https://api-preprod.phonepe.com/apis/hermes'
            self.payment_url = 'https://mercury-t2.phonepe.com/transact'
    
    def generate_checksum(self, payload):
        """Generate PhonePe checksum"""
        payload_str = json.dumps(payload)
        payload_base64 = base64.b64encode(payload_str.encode()).decode()
        string_to_hash = payload_base64 + '/pg/v1/pay' + self.salt_key
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest()
        return checksum, payload_base64
    
    def create_payment(self, order, user):
        """Create PhonePe payment"""
        merchant_transaction_id = f"PP{order.order_number}{uuid.uuid4().hex[:8]}"
        
        payload = {
            'merchantId': self.merchant_id,
            'merchantTransactionId': merchant_transaction_id,
            'merchantUserId': str(user.id),
            'amount': int(order.total * 100),  # Amount in paise
            'redirectUrl': self.callback_url,
            'redirectMode': 'POST',
            'callbackUrl': self.callback_url,
            'mobileNumber': str(user.phone) if user.phone else '',
            'paymentInstrument': {
                'type': 'PAY_PAGE'
            }
        }
        
        checksum, payload_base64 = self.generate_checksum(payload)
        
        return {
            'merchant_id': self.merchant_id,
            'transaction_id': merchant_transaction_id,
            'payload': payload_base64,
            'checksum': checksum,
            'payment_url': self.payment_url
        }
    
    def verify_payment(self, merchant_transaction_id):
        """Verify PhonePe payment"""
        endpoint = f'{self.base_url}/pg/v1/status/{self.merchant_id}/{merchant_transaction_id}'
        string_to_hash = f'/pg/v1/status/{self.merchant_id}/{merchant_transaction_id}{self.salt_key}'
        checksum = hashlib.sha256(string_to_hash.encode()).hexdigest()
        
        headers = {
            'Content-Type': 'application/json',
            'X-VERIFY': checksum + '###' + self.salt_index
        }
        
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None


# PhonePe Views
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from apps.orders.models import Order
from .models import Payment

@login_required
def initiate_phonepe_payment(request, order_id):
    """Initiate PhonePe payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return JsonResponse({'error': 'Order already paid'}, status=400)
    
    phonepe = PhonePePayment()
    payment_data = phonepe.create_payment(order, request.user)
    
    # Save payment record
    payment = Payment.objects.create(
        order=order,
        user=request.user,
        amount=order.total,
        method='phonepe',
        status='pending',
        gateway='phonepe',
        transaction_id=payment_data['transaction_id'],
    )
    
    context = {
        'payment_data': payment_data,
    }
    
    return render(request, 'payments/phonepe_payment.html', context)

@csrf_exempt
@require_POST
def phonepe_callback(request):
    """Handle PhonePe callback"""
    merchant_transaction_id = request.POST.get('merchantTransactionId')
    transaction_id = request.POST.get('transactionId')
    
    phonepe = PhonePePayment()
    verification_data = phonepe.verify_payment(merchant_transaction_id)
    
    if verification_data:
        try:
            payment = Payment.objects.get(transaction_id=merchant_transaction_id)
            
            if verification_data.get('code') == 'PAYMENT_SUCCESS':
                payment.status = 'completed'
                payment.transaction_id = transaction_id
                payment.gateway_response = verification_data
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'paid'
                order.payment_method = 'phonepe'
                order.payment_id = transaction_id
                order.save()
                
                # Send confirmation
                from apps.orders.tasks import send_order_confirmation
                send_order_confirmation.delay(order.id)
            else:
                payment.status = 'failed'
                payment.failure_reason = verification_data.get('message', '')
                payment.gateway_response = verification_data
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'failed'
                order.save()
            
            return redirect('order_detail', order_id=payment.order.id)
            
        except Payment.DoesNotExist:
            return render(request, 'payments/payment_error.html', {
                'error': 'Payment record not found'
            })
    
    return render(request, 'payments/payment_error.html', {
        'error': 'Payment verification failed'
    })