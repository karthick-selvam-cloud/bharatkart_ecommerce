def cart_count(request):
    try:
        if request.user.is_authenticated:
            from .models import Cart
            cart = Cart.objects.filter(user=request.user).first()
        else:
            from .models import Cart
            session_id = request.session.get('cart_session_id')
            cart = Cart.objects.filter(session_id=session_id).first() if session_id else None
        return {'cart_count': cart.get_total_items() if cart else 0}
    except Exception:
        return {'cart_count': 0}