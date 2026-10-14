from .models import Wallet


def wallet(request):
    """Wallet context processor"""
    if request.user.is_authenticated:
        try:
            from .models import Wallet
            wallet_obj, _ = Wallet.objects.get_or_create(user=request.user)
            return {'wallet': wallet_obj}
        except Exception:
            pass
    return {'wallet': None}
