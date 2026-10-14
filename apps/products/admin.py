from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'product_count')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price_display', 'stock_badge', 'is_featured_badge', 'is_active')
    list_filter = ('is_active', 'is_featured', 'is_bestseller', 'category', 'brand', 'gst_rate')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    list_per_page = 30
    list_editable = ('is_active',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'sku', 'category', 'brand')}),
        ('Description', {'fields': ('short_description', 'description')}),
        ('Pricing', {'fields': ('price', 'mrp', 'discount', 'gst_rate')}),
        ('Inventory', {'fields': ('stock', 'min_order_quantity', 'max_order_quantity')}),
        ('Status', {'fields': ('is_active', 'is_featured', 'is_bestseller')}),
        ('Stats (Read Only)', {'fields': ('views_count', 'sales_count', 'average_rating', 'total_ratings'), 'classes': ('collapse',)}),
    )
    
    def price_display(self, obj):
        return format_html(
            '<span style="font-family: Playfair Display, serif; font-weight: 700; '
            'color: #a68a4a; font-size: 1rem;">₹{}</span>',
            obj.price
        )
    price_display.short_description = 'Price'
    
    def stock_badge(self, obj):
        if obj.stock > 20:
            color, label = '#1a3a2e', f'✓ {obj.stock}'
        elif obj.stock > 5:
            color, label = '#c9a961', f'⚠ {obj.stock}'
        elif obj.stock > 0:
            color, label = '#e65100', f'! {obj.stock}'
        else:
            color, label = '#6b1f2c', '✗ Out'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700;">{}</span>',
            color, label
        )
    stock_badge.short_description = 'Stock'
    
    def is_featured_badge(self, obj):
        if obj.is_featured:
            return format_html(
                '<span style="background: linear-gradient(135deg, #c9a961, #a68a4a); '
                'color: white; padding: 4px 10px; border-radius: 12px; '
                'font-size: 0.7rem; font-weight: 700;">★ FEATURED</span>'
            )
        return '—'
    is_featured_badge.short_description = 'Featured'