"""
Product models for BharatKart
"""

from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class Category(models.Model):
    """Product category"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Product brand"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Main product model"""
    GST_CHOICES = [
        ('0', '0%'),
        ('5', '5%'),
        ('12', '12%'),
        ('18', '18%'),
        ('28', '28%'),
    ]

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=500, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    mrp = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    gst_rate = models.CharField(max_length=2, choices=GST_CHOICES, default='18')
    stock = models.PositiveIntegerField(default=0)
    min_order_quantity = models.PositiveIntegerField(default=1)
    max_order_quantity = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_bestseller = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        if self.mrp and self.mrp > 0 and self.price:
            self.discount = ((self.mrp - self.price) / self.mrp) * 100
        super().save(*args, **kwargs)

        def get_main_image(self):
                """Return main image URL"""
        image = self.images.filter(is_main=True).first()
        if image:
            return image.get_url()
        # Fallback to first image
        image = self.images.first()
        if image:
            return image.get_url()
        return None
    def get_main_image(self):
        """Return the URL of the main product image"""
        # Try to find the image marked as main
        image = self.images.filter(is_main=True).first()
        if image:
            return image.get_url()
        # Fallback: use the first image
        image = self.images.first()
        if image:
            return image.get_url()
        return None

    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock > 0


    def is_in_stock(self):
        return self.stock > 0


class ProductImage(models.Model):
    """Product images - supports both uploaded files and external URLs"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # ← NEW
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_main', 'created_at']

    def __str__(self):
        return f"Image for {self.product.name}"

    def get_url(self):
        """Return image URL — either uploaded file or external URL"""
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return None

class ProductVariant(models.Model):
    """Product variants (size, color, etc.)"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"VAR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_final_price(self):
        return self.product.price + self.price_adjustment



class Coupon(models.Model):
    """Discount code shared by cart and order flows."""

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=10,
        choices=[('percent', 'Percentage'), ('fixed', 'Fixed amount')],
        default='percent',
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now
            and (self.valid_until is None or self.valid_until >= now)
            and (self.usage_limit is None or self.used_count < self.usage_limit)
        )