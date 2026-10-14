from paytmchecksum import PaytmChecksum
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
import requests
import json
from datetime import datetime

class PaytmPayment:
    def __init__(self):
        self.merchant_id = settings.PAYTM_MERCHANT_ID
        self.merchant_key = settings.PAYTM_MERCHANT_KEY
        self.website = settings.PAYTM_WEBSITE
        self.industry_type = settings.PAYTM_INDUSTRY_TYPE
        self.channel_id = settings.PAYTM_CHANNEL_ID
        self.callback_url = settings.PAYTM_CALLBACK_URL
    
    def generate_checksum(self, parameters):
        """Generate Paytm checksum"""
        checksum = PaytmChecksum.generateSignature(
            parameters, self.merchant_key
        )
        return checksum
    
    def verify_checksum(self, parameters, checksum):
        """Verify Paytm checksum"""
        return PaytmChecksum.verifySignature(
            parameters, self.merchant_key, checksum
        )
    
    def create_transaction(self, order, user):
        """Create Paytm transaction"""
        transaction_params = {
            'MID': self.merchant_id,
            'ORDER_ID': order.order_number,
            'CUST_ID': str(user.id),
            'INDUSTRY_TYPE_ID': self.industry_type,
            'CHANNEL_ID': self.channel_id,
            'TXN_AMOUNT': str(order.total),
            'WEBSITE': self.website,
            'CALLBACK_URL': self.callback_url,
            'EMAIL': user.email,
            'MOBILE_NO': str(user.phone) if user.phone else '',
            'CHECKSUMHASH': ''
        }
        
        # Generate checksum
        checksum = self.generate_checksum(transaction_params)
        transaction_params['CHECKSUMHASH'] = checksum
        
        return transaction_params
    
    def verify_transaction(self, parameters):
        """Verify transaction status"""
        verification_params = {
            'MID': self.merchant_id,
            'ORDERID': parameters.get('ORDERID'),
            'CHECKSUMHASH': ''
        }
        
        checksum = self.generate_checksum(verification_params)
        verification_params['CHECKSUMHASH'] = checksum
        
        # Make API call to verify
        url = 'https://securegw-stage.paytm.in/order/status'
        response = requests.post(url, json=verification_params)
        
        if response.status_code == 200:
            return response.json()
        return None


# Paytm Views
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from apps.orders.models import Order
from .models import Payment

@login_required
def initiate_paytm_payment(request, order_id):
    """Initiate Paytm payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if order.payment_status == 'paid':
        return JsonResponse({'error': 'Order already paid'}, status=400)
    
    paytm = PaytmPayment()
    transaction_params = paytm.create_transaction(order, request.user)
    
    # Save payment record
    payment = Payment.objects.create(
        order=order,
        user=request.user,
        amount=order.total,
        method='paytm',
        status='pending',
        gateway='paytm',
        transaction_id=order.order_number,
    )
    
    context = {
        'params': transaction_params,
        'payment_url': 'https://securegw-stage.paytm.in/order/process'
    }
    
    return render(request, 'payments/paytm_payment.html', context)

@csrf_exempt
@require_POST
def paytm_callback(request):
    """Handle Paytm callback"""
    form_data = request.POST.dict()
    checksum = form_data.pop('CHECKSUMHASH', '')
    
    paytm = PaytmPayment()
    
    if paytm.verify_checksum(form_data, checksum):
        order_id = form_data.get('ORDERID')
        txn_id = form_data.get('TXNID')
        status = form_data.get('STATUS')
        amount = form_data.get('TXNAMOUNT')
        
        try:
            payment = Payment.objects.get(transaction_id=order_id)
            
            if status == 'TXN_SUCCESS':
                payment.status = 'completed'
                payment.transaction_id = txn_id
                payment.gateway_response = form_data
                payment.save()
                
                # Update order
                order = payment.order
                order.payment_status = 'paid'
                order.payment_method = 'paytm'
                order.payment_id = txn_id
                order.save()
                
                # Send confirmation
                from apps.orders.tasks import send_order_confirmation
                send_order_confirmation.delay(order.id)
            else:
                payment.status = 'failed'
                payment.failure_reason = form_data.get('RESPMSG', '')
                payment.gateway_response = form_data
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
        'error': 'Checksum verification failed'
    })