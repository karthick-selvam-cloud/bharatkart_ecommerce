from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Wishlist, WishlistItem
from apps.products.models import Product


@login_required
def wishlist_detail(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related('product').all()
    return render(request, 'wishlist/wishlist.html', {
        'wishlist': wishlist,
        'items': items,
    })


@login_required
@require_POST
def toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    if not created:
        item.delete()
        return JsonResponse({'success': True, 'in_wishlist': False})
    return JsonResponse({'success': True, 'in_wishlist': True})


@login_required
@require_POST
def remove(request, item_id):
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    messages.success(request, 'Item removed from wishlist')
    return redirect('wishlist:detail')