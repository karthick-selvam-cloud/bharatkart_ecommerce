from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.orders.models import Order


@login_required
def payment_page(request, order_id):
    """Payment method selection page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/payment_page.html', {'order': order})


@login_required
def payment_success(request, order_id):
    """Mark order as paid and confirm"""
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Update order status
    order.payment_status = 'paid'
    order.status = 'confirmed'
    order.save()

    messages.success(request, f'Payment successful! Order {order.order_number} confirmed.')
    return render(request, 'payments/payment_success.html', {'order': order})


def payment_error(request):
    return render(request, 'payments/payment_error.html')