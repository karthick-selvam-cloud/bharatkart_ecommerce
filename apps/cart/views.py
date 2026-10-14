from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
import uuid

from .models import Cart, CartItem
from apps.products.models import Product
from apps.orders.models import Order, OrderItem


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['cart_session_id'] = session_id
        cart, _ = Cart.objects.get_or_create(session_id=session_id)
    return cart


def cart_detail(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    return render(request, 'cart/cart_detail.html', {
        'cart': cart,
        'items': items,
    })


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        import json
        body = json.loads(request.body) if request.body else {}
    except Exception:
        body = {}
    quantity = int(body.get('quantity', 1))

    if product.stock < quantity:
        return JsonResponse({'success': False, 'error': 'Insufficient stock'}, status=400)

    cart = get_or_create_cart(request)
    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return JsonResponse({
        'success': True,
        'message': 'Added to your bag',
        'cart_count': cart.get_total_items(),
        'cart_total': str(cart.get_subtotal()),
    })


@require_POST
def update_item(request, item_id):
    import json
    try:
        body = json.loads(request.body)
        quantity = int(body.get('quantity', 1))
    except Exception:
        quantity = 1

    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if quantity <= 0:
        item.delete()
        return JsonResponse({
            'success': True,
            'removed': True,
            'cart_total': str(cart.get_subtotal()),
        })

    item.quantity = quantity
    item.save()

    return JsonResponse({
        'success': True,
        'item_total': str(item.get_total_price()),
        'cart_total': str(cart.get_subtotal()),
    })


@require_POST
def remove_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, 'Item removed from bag')
    return redirect('cart:detail')


# ============================================================
# CHECKOUT — CREATE ORDER AND REDIRECT TO PAYMENT
# ============================================================

@login_required
def checkout(request):
    """Show checkout page (address confirmation)"""
    cart = get_or_create_cart(request)
    if cart.get_total_items() == 0:
        messages.warning(request, 'Your bag is empty')
        return redirect('cart:detail')

    return render(request, 'cart/checkout.html', {'cart': cart})


@login_required
@require_POST
def place_order(request):
    """Create Order from cart and redirect to payment"""
    cart = get_or_create_cart(request)
    
    if cart.get_total_items() == 0:
        messages.error(request, 'Your bag is empty')
        return redirect('cart:detail')

    try:
        with transaction.atomic():
            # Calculate totals
            subtotal = cart.get_subtotal()
            gst = cart.get_gst_total()
            shipping = Decimal('0.00')
            total = subtotal + gst + shipping

            # Create Order
            order = Order.objects.create(
                user=request.user,
                status='pending',
                payment_status='pending',
                subtotal=subtotal,
                gst=gst,
                shipping_charges=shipping,
                total=total,
            )

            # Create OrderItems from CartItems
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    unit_price=item.get_unit_price(),
                    total_price=item.get_total_price(),
                )

            # Clear cart
            cart.items.all().delete()

        messages.success(request, f'Order {order.order_number} created! Complete payment to confirm.')
        return redirect('payments:page', order_id=order.id)

    except Exception as e:
        messages.error(request, f'Something went wrong: {e}')
        return redirect('cart:detail')