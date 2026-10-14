from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product
import uuid

User = get_user_model()

class UserInteraction(models.Model):
    """Track user interactions for recommendations"""
    INTERACTION_TYPE_CHOICES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('cart_add', 'Add to Cart'),
        ('purchase', 'Purchase'),
        ('wishlist', 'Wishlist'),
        ('search', 'Search'),
        ('review', 'Review'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    weight = models.FloatField(default=1.0)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'interaction_type']),
            models.Index(fields=['product', 'interaction_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.interaction_type}"


class ProductSimilarity(models.Model):
    """Store product similarity scores"""
    product1 = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similarity_from')
    product2 = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='similarity_to')
    similarity_score = models.FloatField()
    similarity_type = models.CharField(max_length=50, default='content')  # content, collaborative
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product1', 'product2', 'similarity_type']
        indexes = [
            models.Index(fields=['product1', 'similarity_score']),
        ]
    
    def __str__(self):
        return f"{self.product1.name} - {self.product2.name}: {self.similarity_score}"


class UserEmbedding(models.Model):
    """Store user embeddings for recommendations"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='embedding')
    embedding = models.JSONField(default=list)
    dimension = models.IntegerField(default=128)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Embedding for {self.user.username}"


class ProductEmbedding(models.Model):
    """Store product embeddings for recommendations"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='embedding')
    embedding = models.JSONField(default=list)
    dimension = models.IntegerField(default=128)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Embedding for {self.product.name}"


class RecommendationCache(models.Model):
    """Cache recommendations for quick retrieval"""
    RECOMMENDATION_TYPE_CHOICES = [
        ('personalized', 'Personalized'),
        ('similar_products', 'Similar Products'),
        ('trending', 'Trending'),
        ('frequently_bought', 'Frequently Bought Together'),
        ('recently_viewed', 'Recently Viewed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    recommendation_type = models.CharField(max_length=50, choices=RECOMMENDATION_TYPE_CHOICES)
    recommended_products = models.JSONField(default=list)
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'recommendation_type']),
            models.Index(fields=['product', 'recommendation_type']),
        ]
    
    def is_valid(self):
        from django.utils import timezone
        return self.expires_at > timezone.now()