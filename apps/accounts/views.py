"""
Account views for BharatKart
"""
import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Sum
from django.db import transaction
from decimal import Decimal, InvalidOperation
from .models import User, Address, Wallet, WalletTransaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt



@require_http_methods(["GET", "POST"])
def login_view(request):
    """Luxury login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)

        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'accounts/login.html', {'email': email})

        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            username = email

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'accounts:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'accounts/login.html')


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Luxury registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        errors = []

        if not all([first_name, last_name, email, password, password2]):
            errors.append('Please fill in all required fields.')

        if password != password2:
            errors.append('Passwords do not match.')

        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')

        if User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/register.html', {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
            })

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        login(request, user)
        messages.success(request, f'Welcome to BharatKart, {first_name}!')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html')


def logout_view(request):
    """Logout view"""
    user_name = request.user.first_name if request.user.is_authenticated else 'Guest'
    logout(request)
    messages.success(request, f'Goodbye {user_name}! You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_view(request):
    """Luxury account dashboard"""
    user = request.user
    wallet, _ = Wallet.objects.get_or_create(user=user)

    # Get user stats
    try:
        orders_count = user.orders.count()
        total_spent = user.orders.filter(
            payment_status='paid'
        ).aggregate(total=Sum('total'))['total'] or 0
    except Exception:
        orders_count = 0
        total_spent = 0

    try:
        wishlist_count = user.wishlists.aggregate(
            count=Count('items')
        )['count'] or 0
    except Exception:
        wishlist_count = 0

    try:
        addresses_count = user.addresses.count()
    except Exception:
        addresses_count = 0

    # Recent orders
    try:
        recent_orders = user.orders.all().order_by('-created_at')[:5]
    except Exception:
        recent_orders = []

    context = {
        'user': user,
        'orders_count': orders_count,
        'total_spent': total_spent,
        'wishlist_count': wishlist_count,
        'addresses_count': addresses_count,
        'recent_orders': recent_orders,
        'wallet': wallet,
        'wallet_transactions': wallet.transactions.all()[:5],
    }
    return render(request, 'accounts/dashboard.html', context)


# ============================================================
# WALLET VIEWS
# ============================================================

@login_required
def wallet_view(request):
    """Wallet dashboard with balance and transaction history"""
    from .models import Wallet, WalletTransaction
    from decimal import Decimal
    
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    
    # Get filter parameters
    txn_filter = request.GET.get('type', 'all')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset
    transactions = wallet.transactions.all()
    
    # Apply filter
    if txn_filter == 'credit':
        transactions = transactions.filter(
            transaction_type__in=['credit', 'refund', 'cashback', 'bonus']
        )
    elif txn_filter == 'debit':
        transactions = transactions.filter(
            transaction_type__in=['debit', 'withdrawal']
        )
    
    # Apply sort
    if sort_by == 'oldest':
        transactions = transactions.order_by('created_at')
    elif sort_by == 'amount_high':
        transactions = transactions.order_by('-amount')
    elif sort_by == 'amount_low':
        transactions = transactions.order_by('amount')
    else:
        transactions = transactions.order_by('-created_at')
    
    # Stats
    total_added = wallet.total_added
    total_spent = wallet.total_spent
    total_transactions = wallet.transactions.count()
    credit_count = wallet.transactions.filter(
        transaction_type__in=['credit', 'refund', 'cashback', 'bonus']
    ).count()
    debit_count = wallet.transactions.filter(
        transaction_type__in=['debit', 'withdrawal']
    ).count()
    
    # Recent transactions (5)
    recent_transactions = wallet.transactions.all()[:5]
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
        'recent_transactions': recent_transactions,
        'total_added': total_added,
        'total_spent': total_spent,
        'total_transactions': total_transactions,
        'credit_count': credit_count,
        'debit_count': debit_count,
        'txn_filter': txn_filter,
        'sort_by': sort_by,
    }
    return render(request, 'accounts/wallet.html', context)


@login_required
@require_POST
def add_money_view(request):
    """Add money to wallet"""
    from .models import Wallet
    from django.http import JsonResponse
    from decimal import Decimal, InvalidOperation
    import json
    
    try:
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', 0)))
        payment_method = data.get('payment_method', 'upi')
    except (json.JSONDecodeError, InvalidOperation, TypeError):
        return JsonResponse({
            'success': False,
            'error': 'Invalid amount'
        }, status=400)
    
    # Validate amount
    if amount <= 0:
        return JsonResponse({
            'success': False,
            'error': 'Amount must be greater than 0'
        }, status=400)
    
    if amount > 100000:
        return JsonResponse({
            'success': False,
            'error': 'Maximum ₹1,00,000 per transaction'
        }, status=400)
    
    if amount < 100:
        return JsonResponse({
            'success': False,
            'error': 'Minimum ₹100 required'
        }, status=400)
    
    # Get or create wallet
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    # Credit wallet
    try:
        new_balance = wallet.credit(
            amount=amount,
            description=f'Money added via {payment_method.upper()}',
            transaction_type='credit'
        )
        
        return JsonResponse({
            'success': True,
            'message': f'₹{amount} added successfully!',
            'new_balance': str(new_balance),
            'amount': str(amount),
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def transaction_history_view(request):
    """Full transaction history page"""
    from .models import Wallet
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    transactions = wallet.transactions.all()
    
    context = {
        'wallet': wallet,
        'transactions': transactions,
    }
    return render(request, 'accounts/transaction_history.html', context)


@login_required
def wallet_context(request):
    """Context processor helper"""
    try:
        from .models import Wallet
        wallet = Wallet.objects.filter(user=request.user).first()
        return {'wallet': wallet}
    except Exception:
        return {'wallet': None}


@login_required
def profile_view(request):
    """Luxury edit profile view"""
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.phone = request.POST.get('phone', user.phone).strip()
        user.gender = request.POST.get('gender', user.gender)
        dob = request.POST.get('date_of_birth', '')
        if dob:
            user.date_of_birth = dob
        user.address_line1 = request.POST.get('address_line1', user.address_line1).strip()
        user.address_line2 = request.POST.get('address_line2', user.address_line2).strip()
        user.city = request.POST.get('city', user.city).strip()
        user.state = request.POST.get('state', user.state).strip()
        user.pincode = request.POST.get('pincode', user.pincode).strip()

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {'user': user})


@login_required
def change_password_view(request):
    """Change password view"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not request.user.check_password(old_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:dashboard')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:dashboard')

        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('accounts:dashboard')

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Password changed successfully!')
        return redirect('accounts:dashboard')

    return redirect('accounts:dashboard')

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


@login_required
@require_POST
def set_default_address_view(request, address_id):
    """Set an address as default"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    
    # Unset all other defaults
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Set this one as default
    address.is_default = True
    address.save()
    
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_address_view(request, address_id):
    """Delete an address"""
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    
    return JsonResponse({'success': True})

@login_required
def addresses_view(request):
    """Manage addresses view"""
    addresses = request.user.addresses.all()
    return render(request, 'accounts/addresses.html', {
        'addresses': addresses
    })

@login_required
@require_POST
def cancel_order_view(request, order_id):
    """Cancel a pending order"""
    from apps.orders.models import Order
    
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)
    
    if order.status not in ['pending', 'confirmed']:
        return JsonResponse({
            'success': False, 
            'error': 'This order cannot be cancelled'
        }, status=400)
    
    order.status = 'cancelled'
    order.save()
    
    return JsonResponse({'success': True, 'message': 'Order cancelled'})

# ============================================================
# MY ORDERS VIEWS
# ============================================================

@login_required
def my_orders_view(request):
    """User's order history with luxury design"""
    from apps.orders.models import Order
    
    # Get filter params
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset
    orders = Order.objects.filter(user=request.user)
    
    # Apply status filter
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    # Apply search
    if search_query:
        orders = orders.filter(order_number__icontains=search_query)
    
    # Apply sorting
    sort_map = {
        'newest': '-created_at',
        'oldest': 'created_at',
        'price_high': '-total',
        'price_low': 'total',
    }
    orders = orders.order_by(sort_map.get(sort_by, '-created_at'))
    
    # Compute stats
    all_orders = Order.objects.filter(user=request.user)
    total_orders = all_orders.count()
    total_spent = all_orders.aggregate(total=Sum('total'))['total'] or 0
    pending_count = all_orders.filter(status='pending').count()
    delivered_count = all_orders.filter(status='delivered').count()
    cancelled_count = all_orders.filter(status='cancelled').count()
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'pending_count': pending_count,
        'delivered_count': delivered_count,
        'cancelled_count': cancelled_count,
        'status_filter': status_filter,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required
def account_order_detail_view(request, order_id):
    """Detailed order view inside account"""
    from apps.orders.models import Order
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Progress calculation
    status_progress = {
        'pending': 20,
        'confirmed': 40,
        'processing': 60,
        'shipped': 80,
        'out_for_delivery': 90,
        'delivered': 100,
        'cancelled': 0,
    }
    progress = status_progress.get(order.status, 0)
    
    context = {
        'order': order,
        'progress': progress,
        'order_items': order.items.all(),
    }
    return render(request, 'accounts/order_detail.html', context)
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from decimal import Decimal
from .models import Wallet, WalletTransaction


@login_required
def wallet_view(request):
    """Wallet page"""
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all()[:20]
    return render(request, 'accounts/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
    })


@login_required
@require_POST
def wallet_create_order(request):
    """Create Razorpay order for wallet top-up"""
    try:
        import json
        data = json.loads(request.body)
        amount = Decimal(str(data.get('amount', 0)))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid amount'}, status=400)

    if amount < 1:
        return JsonResponse({'success': False, 'error': 'Minimum ₹1 required'}, status=400)

    if amount > 100000:
        return JsonResponse({'success': False, 'error': 'Maximum ₹1,00,000 allowed'}, status=400)

    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    # Create WalletTransaction first
    transaction = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='credit',
        status='pending',
        description=f'Wallet top-up ₹{amount}',
    )

    # Try Razorpay if keys are configured
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET,
            ))
            razorpay_order = client.order.create({
                'amount': int(amount * 100),  # paise
                'currency': 'INR',
                'receipt': f'WALLET-{transaction.id}',
                'notes': {
                    'user_id': request.user.id,
                    'transaction_id': transaction.id,
                    'type': 'wallet_topup',
                },
            })
            transaction.razorpay_order_id = razorpay_order['id']
            transaction.save()

            return JsonResponse({
                'success': True,
                'order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': 'INR',
                'key': settings.RAZORPAY_KEY_ID,
                'transaction_id': transaction.id,
                'user': {
                    'name': f'{request.user.first_name} {request.user.last_name}'.strip() or request.user.username,
                    'email': request.user.email,
                    'contact': str(request.user.phone) if request.user.phone else '',
                },
            })
        except Exception as e:
            transaction.status = 'failed'
            transaction.save()
            return JsonResponse({'success': False, 'error': f'Razorpay error: {e}'}, status=500)
    else:
        # Demo mode — instant top-up without real payment
        wallet.add_balance(amount)
        transaction.status = 'success'
        transaction.razorpay_payment_id = f'DEMO-{transaction.id}'
        transaction.save()

        return JsonResponse({
            'success': True,
            'demo_mode': True,
            'message': f'₹{amount} added to wallet (demo mode)',
            'new_balance': str(wallet.balance),
        })


@csrf_exempt
@login_required
@require_POST
def wallet_verify_payment(request):
    """Verify Razorpay payment and update wallet"""
    try:
        import json
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
    except Exception:
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

    try:
        transaction = WalletTransaction.objects.get(id=transaction_id, wallet__user=request.user)
    except WalletTransaction.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Transaction not found'}, status=404)

    # Verify signature
    try:
        client = razorpay.Client(auth=(
            settings.RAZORPAY_KEY_ID,
            settings.RAZORPAY_KEY_SECRET,
        ))
        client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        })
    except Exception as e:
        transaction.status = 'failed'
        transaction.save()
        return JsonResponse({'success': False, 'error': 'Payment signature verification failed'}, status=400)

    # Add balance
    wallet = transaction.wallet
    wallet.add_balance(transaction.amount)
    transaction.status = 'success'
    transaction.razorpay_payment_id = razorpay_payment_id
    transaction.save()

    return JsonResponse({
        'success': True,
        'message': f'₹{transaction.amount} added to wallet',
        'new_balance': str(wallet.balance),
    })


@login_required
@require_POST
def wallet_add_view(request):
    """Legacy manual add — kept for backward compatibility"""
    try:
        amount = Decimal(request.POST.get('amount', 0))
    except Exception:
        amount = Decimal('0')

    if amount < 1:
        messages.error(request, 'Please enter a valid amount')
        return redirect('accounts:wallet')

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.add_balance(amount)
    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type='credit',
        status='success',
        description=f'Manual top-up ₹{amount}',
    )
    messages.success(request, f'₹{amount} added to your wallet')
    return redirect('accounts:wallet')


@login_required
@require_POST
def cancel_order_view(request, order_id):
    """Cancel an order"""
    from apps.orders.models import Order
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)

    if order.status not in ['pending', 'confirmed']:
        return JsonResponse({'success': False, 'error': 'This order cannot be cancelled'}, status=400)

    order.status = 'cancelled'
    order.save()
    return JsonResponse({'success': True, 'message': 'Order cancelled'})


@login_required
def my_orders_view(request):
    from apps.orders.models import Order
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required
def account_order_detail_view(request, order_id):
    from apps.orders.models import Order
    from django.shortcuts import get_object_or_404
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# Context processor for wallet balance (used by templates)
def wallet_context(request):
    if request.user.is_authenticated:
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return {'wallet': wallet}
    return {'wallet': None}

