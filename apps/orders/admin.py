from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'unit_price', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user_email', 'status_badge', 'payment_badge', 'total_display', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_per_page = 30
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Customer'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#c9a961',
            'confirmed': '#4facfe',
            'processing': '#e65100',
            'shipped': '#4527a0',
            'out_for_delivery': '#00838f',
            'delivered': '#1a3a2e',
            'cancelled': '#6b1f2c',
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700; '
            'text-transform: uppercase; letter-spacing: 0.05em;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_badge(self, obj):
        if obj.payment_status == 'paid':
            color, label = '#1a3a2e', '✓ PAID'
        elif obj.payment_status == 'pending':
            color, label = '#c9a961', '⏳ PENDING'
        else:
            color, label = '#6b1f2c', '✗ FAILED'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700;">{}</span>',
            color, label
        )
    payment_badge.short_description = 'Payment'
    
    def total_display(self, obj):
        return format_html(
            '<span style="font-family: Playfair Display, serif; font-weight: 700; '
            'color: #a68a4a; font-size: 1rem;">₹{}</span>',
            obj.total
        )
    total_display.short_description = 'Total'