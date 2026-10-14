"""
RAG models for BharatKart AI Concierge
"""

from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class KnowledgeBase(models.Model):
    """Knowledge base articles for RAG"""
    CATEGORY_CHOICES = [
        ('product', 'Product Information'),
        ('order', 'Order Related'),
        ('shipping', 'Shipping & Delivery'),
        ('returns', 'Returns & Refunds'),
        ('payment', 'Payment Issues'),
        ('wallet', 'Wallet & Balance'),
        ('account', 'Account Related'),
        ('faq', 'FAQ'),
        ('other', 'Other'),
    ]
    
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=500)
    content = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='faq')
    keywords = models.CharField(max_length=500, blank=True, help_text="Comma-separated keywords")
    tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    views_count = models.PositiveIntegerField(default=0)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_keywords_list(self):
        return [k.strip().lower() for k in self.keywords.split(',') if k.strip()]


class ChatSession(models.Model):
    """Chat session for tracking conversations"""
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_sessions')
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255, blank=True)
    context = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.username if self.user else 'Guest'} — {self.session_id[:8]}"


class ChatMessage(models.Model):
    """Individual chat messages"""
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('product', 'Product Card'),
        ('order', 'Order Card'),
        ('action', 'Action Button'),
        ('quick_replies', 'Quick Replies'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    is_user = models.BooleanField(default=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default='text')
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)  # For product cards, order info, etc.
    intent = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.content[:50]}"


class UserPreference(models.Model):
    """Track user preferences for personalization"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_preferences')
    favorite_categories = models.JSONField(default=list, blank=True)
    price_range_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_range_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    preferred_brands = models.JSONField(default=list, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"