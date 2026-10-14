from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Address, SellerProfile, Wallet, WalletTransaction
from django.contrib.admin import AdminSite
from django.db.models import Sum, Count

# Override the default AdminSite with custom dashboard
class BharatKartAdminSite(AdminSite):
    site_header = "BharatKart Administration"
    site_title = "BharatKart Admin"
    index_title = "Welcome to BharatKart"
    index_template = "admin/index.html"

    def index(self, request, extra_context=None):
        from apps.products.models import Product
        from apps.orders.models import Order
        
        extra_context = extra_context or {}
        
        try:
            extra_context['total_products'] = Product.objects.filter(is_active=True).count()
        except Exception:
            extra_context['total_products'] = 0
        
        try:
            extra_context['total_orders'] = Order.objects.count()
        except Exception:
            extra_context['total_orders'] = 0
        
        try:
            extra_context['total_users'] = User.objects.filter(role='customer').count()
        except Exception:
            extra_context['total_users'] = 0
        
        try:
            revenue = Order.objects.filter(payment_status='paid').aggregate(
                total=Sum('total')
            )['total'] or 0
            extra_context['total_revenue'] = revenue
        except Exception:
            extra_context['total_revenue'] = 0
        
        try:
            extra_context['recent_orders'] = Order.objects.select_related('user').order_by('-created_at')[:5]
        except Exception:
            extra_context['recent_orders'] = []
        
        try:
            extra_context['recent_users'] = User.objects.order_by('-date_joined')[:5]
        except Exception:
            extra_context['recent_users'] = []
        
        return super().index(request, extra_context)


# Uncomment to use custom admin site
# admin.site.__class__ = BharatKartAdminSite



@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'full_name', 'role_badge', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'gender', 'date_of_birth', 'profile_picture')}),
        ('Address', {'fields': ('address_line1', 'address_line2', 'city', 'state', 'pincode')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_phone_verified', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or '—'
    full_name.short_description = 'Full Name'
    
    def role_badge(self, obj):
        colors = {
            'customer': '#4facfe',
            'seller': '#c9a961',
            'admin': '#6b1f2c',
            'delivery': '#43e97b',
        }
        color = colors.get(obj.role, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700; '
            'text-transform: uppercase; letter-spacing: 0.05em;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user_email', 'city', 'pincode', 'address_type', 'is_default_badge')
    list_filter = ('address_type', 'is_default', 'city', 'state')
    search_fields = ('full_name', 'user__email', 'city', 'pincode')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def is_default_badge(self, obj):
        if obj.is_default:
            return format_html(
                '<span style="background: linear-gradient(135deg, #c9a961, #a68a4a); color: white; '
                'padding: 4px 10px; border-radius: 12px; font-size: 0.7rem; font-weight: 700;">★ DEFAULT</span>'
            )
        return '—'
    is_default_badge.short_description = 'Default'


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('store_name', 'user_email', 'is_verified_badge', 'rating', 'total_ratings')
    list_filter = ('is_verified',)
    search_fields = ('store_name', 'user__email', 'gst_number')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Owner'
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="background: #1a3a2e; color: white; padding: 4px 10px; '
                'border-radius: 12px; font-size: 0.7rem; font-weight: 700;">✓ VERIFIED</span>'
            )
        return format_html(
            '<span style="background: #999; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700;">PENDING</span>'
        )
    is_verified_badge.short_description = 'Status'


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'balance_display', 'total_added_display', 'total_spent_display', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 30
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    
    def balance_display(self, obj):
        return format_html(
            '<span style="font-family: Playfair Display, serif; font-size: 1.1rem; '
            'font-weight: 700; color: #a68a4a;">₹{}</span>',
            obj.balance
        )
    balance_display.short_description = 'Balance'
    
    def total_added_display(self, obj):
        return format_html('<span style="color: #1a3a2e; font-weight: 600;">₹{}</span>', obj.total_added)
    total_added_display.short_description = 'Added'
    
    def total_spent_display(self, obj):
        return format_html('<span style="color: #6b1f2c; font-weight: 600;">₹{}</span>', obj.total_spent)
    total_spent_display.short_description = 'Spent'


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet_user', 'type_badge', 'amount_display', 'balance_after', 'description_short', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('wallet__user__email', 'description', 'reference_id')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50
    
    def wallet_user(self, obj):
        return obj.wallet.user.email
    wallet_user.short_description = 'User'
    
    def type_badge(self, obj):
        colors = {
            'credit': '#1a3a2e',
            'debit': '#6b1f2c',
            'refund': '#c9a961',
            'cashback': '#4facfe',
            'bonus': '#c9a961',
            'withdrawal': '#e65100',
        }
        color = colors.get(obj.transaction_type, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700; '
            'text-transform: uppercase;">{}</span>',
            color, obj.get_transaction_type_display()
        )
    type_badge.short_description = 'Type'
    
    def amount_display(self, obj):
        sign = '+' if obj.is_credit else '-'
        color = '#1a3a2e' if obj.is_credit else '#6b1f2c'
        return format_html(
            '<span style="font-family: Playfair Display, serif; font-weight: 700; '
            'color: {}; font-size: 1rem;">{}₹{}</span>',
            color, sign, obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def description_short(self, obj):
        if len(obj.description) > 40:
            return obj.description[:40] + '...'
        return obj.description or '—'
    description_short.short_description = 'Description'


# ============ CUSTOMIZE ADMIN SITE HEADER ============
admin.site.site_header = "BharatKart Administration"
admin.site.site_title = "BharatKart Admin"
admin.site.index_title = "Welcome to BharatKart Administration"