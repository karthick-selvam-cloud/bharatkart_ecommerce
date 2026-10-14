from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Min, Max
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Product, Category, Brand


class HomeView(TemplateView):
    template_name = 'products/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_products'] = Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('category', 'brand')[:12]
        context['bestsellers'] = Product.objects.filter(
            is_active=True, is_bestseller=True
        ).select_related('category', 'brand')[:8]
        context['new_arrivals'] = Product.objects.filter(
            is_active=True
        ).select_related('category', 'brand').order_by('-created_at')[:12]
        context['categories'] = Category.objects.filter(
            parent=None, is_active=True
        )[:10]
        return context


class ProductListView(ListView):
    """Universal luxury product listing — handles all category pages"""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 24

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related(
            'category', 'brand', 'category__parent'
        )

        # Search
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__name__icontains=search) |
                Q(category__name__icontains=search)
            )

        # Category filter — check both self and parent
        category = self.request.GET.get('category', '').strip()
        if category:
            queryset = queryset.filter(
                Q(category__slug=category) | Q(category__parent__slug=category)
            )

        # Brand filter
        brand = self.request.GET.get('brand', '').strip()
        if brand:
            queryset = queryset.filter(brand__slug=brand)

        # Price filter
        try:
            min_price = self.request.GET.get('min_price', '')
            max_price = self.request.GET.get('max_price', '')
            if min_price:
                queryset = queryset.filter(price__gte=float(min_price))
            if max_price:
                queryset = queryset.filter(price__lte=float(max_price))
        except ValueError:
            pass

        # Rating filter
        try:
            min_rating = self.request.GET.get('min_rating', '')
            if min_rating:
                queryset = queryset.filter(average_rating__gte=float(min_rating))
        except ValueError:
            pass

        # Availability
        availability = self.request.GET.get('availability', '')
        if availability == 'in_stock':
            queryset = queryset.filter(stock__gt=0)
        elif availability == 'out_of_stock':
            queryset = queryset.filter(stock=0)

        # Feature filter
        if self.request.GET.get('featured') == '1':
            queryset = queryset.filter(is_featured=True)
        if self.request.GET.get('bestseller') == '1':
            queryset = queryset.filter(is_bestseller=True)

        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        sort_map = {
            'newest': '-created_at',
            'oldest': 'created_at',
            'price_low': 'price',
            'price_high': '-price',
            'rating': '-average_rating',
            'popular': '-sales_count',
            'discount': '-discount',
        }
        queryset = queryset.order_by(sort_map.get(sort, '-created_at'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Base context
        context['all_categories'] = Category.objects.filter(
            parent=None, is_active=True
        ).prefetch_related('children')
        context['all_brands'] = Brand.objects.filter(is_active=True)[:30]

        # Current filters
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_brand'] = self.request.GET.get('brand', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['min_rating'] = self.request.GET.get('min_rating', '')
        context['availability'] = self.request.GET.get('availability', '')

        # Price range from DB
        price_range = Product.objects.filter(is_active=True).aggregate(
            min_p=Min('price'), max_p=Max('price')
        )
        context['price_min'] = int(price_range['min_p'] or 0)
        context['price_max'] = int(price_range['max_p'] or 500000)

        # Category-specific page hero
        cat_slug = self.request.GET.get('category', '')
        sort_param = self.request.GET.get('sort', '')

        if cat_slug:
            cat_obj = Category.objects.filter(slug=cat_slug).first()
            if cat_obj:
                context['page_title'] = cat_obj.name
                context['page_subtitle'] = f"Explore our curated {cat_obj.name.lower()} collection"
                context['page_icon'] = self._category_icon(cat_obj.slug)
                context['current_category_obj'] = cat_obj
        elif sort_param == 'discount':
            context['page_title'] = 'Luxury Sale'
            context['page_subtitle'] = 'Exclusive savings on premium products'
            context['page_icon'] = 'fa-gem'
        elif self.request.GET.get('featured') == '1':
            context['page_title'] = 'Featured Selection'
            context['page_subtitle'] = 'Handpicked masterpieces for the discerning shopper'
            context['page_icon'] = 'fa-star'
        else:
            context['page_title'] = 'All Collections'
            context['page_subtitle'] = "Discover timeless elegance from India's finest brands"
            context['page_icon'] = 'fa-th-large'

        return context

    def _category_icon(self, slug):
        icons = {
            'electronics': 'fa-mobile-alt',
            'fashion': 'fa-tshirt',
            'home-living': 'fa-couch',
            'beauty': 'fa-spa',
            'sports': 'fa-dumbbell',
            'books': 'fa-book',
            'smartphones': 'fa-mobile-alt',
            'laptops': 'fa-laptop',
            'headphones': 'fa-headphones',
            'smartwatches': 'fa-clock',
            'cameras': 'fa-camera',
            'mens-fashion': 'fa-user-tie',
            'womens-fashion': 'fa-female',
            'footwear': 'fa-shoe-prints',
            'accessories': 'fa-gem',
            'furniture': 'fa-couch',
            'kitchen': 'fa-utensils',
            'decor': 'fa-palette',
            'bedding': 'fa-bed',
            'skincare': 'fa-spa',
            'makeup': 'fa-paint-brush',
            'fragrances': 'fa-spray-can',
            'haircare': 'fa-cut',
        }
        return icons.get(slug, 'fa-box')


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related(
            'category', 'brand'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        product.views_count += 1
        product.save(update_fields=['views_count'])

        # Related products from same category
        context['related_products'] = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id).select_related('brand')[:8]

        # Similar from same brand
        if product.brand:
            context['similar_products'] = Product.objects.filter(
                brand=product.brand, is_active=True
            ).exclude(id=product.id)[:4]

        return context


@require_POST
def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'login_required'}, status=401)
    from apps.wishlist.models import Wishlist, WishlistItem
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    if not created:
        item.delete()
        return JsonResponse({'success': True, 'in_wishlist': False})
    return JsonResponse({'success': True, 'in_wishlist': True})