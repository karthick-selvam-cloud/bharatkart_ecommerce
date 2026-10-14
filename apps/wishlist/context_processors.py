def wishlist_count(request):
    try:
        if request.user.is_authenticated:
            from .models import Wishlist
            wishlist = Wishlist.objects.filter(user=request.user).first()
            return {'wishlist_count': wishlist.get_total_items() if wishlist else 0}
    except Exception:
        pass
    return {'wishlist_count': 0}