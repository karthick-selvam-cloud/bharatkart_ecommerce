"""
Cart models for BharatKart
"""

from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product, ProductVariant

User = get_user_model()


class Cart(models.Model):
    """Shopping cart"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True
    )
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username if self.user else 'Guest'}"

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def get_subtotal(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_gst_total(self):
        return sum(item.get_gst_amount() for item in self.items.all())

    def get_grand_total(self):
        return self.get_subtotal() + self.get_gst_total()


class CartItem(models.Model):
    """Items in cart"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_unit_price(self):
        if self.variant:
            return self.variant.get_final_price()
        return self.product.price

    def get_total_price(self):
        return self.get_unit_price() * self.quantity

    def get_gst_amount(self):
        try:
            gst_rate = Decimal(self.product.gst_rate)
            return (self.get_total_price() * gst_rate / 100).quantize(Decimal('0.01'))
        except Exception:
            return Decimal('0.00')