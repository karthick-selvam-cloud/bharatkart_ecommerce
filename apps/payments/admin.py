from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order_number', 'amount_display', 'status_badge', 'gateway', 'created_at')
    list_filter = ('status', 'gateway', 'method')
    search_fields = ('transaction_id', 'order__order_number')
    readonly_fields = ('created_at',)
    
    def order_number(self, obj):
        return obj.order.order_number
    order_number.short_description = 'Order'
    
    def amount_display(self, obj):
        return format_html(
            '<span style="font-family: Playfair Display, serif; font-weight: 700; '
            'color: #a68a4a;">₹{}</span>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {'completed': '#1a3a2e', 'pending': '#c9a961', 'failed': '#6b1f2c', 'refunded': '#4facfe'}
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 10px; '
            'border-radius: 12px; font-size: 0.7rem; font-weight: 700; '
            'text-transform: uppercase;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'