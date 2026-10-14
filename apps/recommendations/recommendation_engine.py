import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from django.db.models import Q, Count, Avg
from django.core.cache import cache
from apps.products.models import Product, Category
from apps.orders.models import Order, OrderItem
from .models import UserInteraction, ProductSimilarity, RecommendationCache
import logging

logger = logging.getLogger(__name__)

class RecommendationEngine:
    """ML-based recommendation engine"""
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.max_recommendations = 12
    
    def get_personalized_recommendations(self, user, limit=None):
        """Get personalized recommendations for user"""
        limit = limit or self.max_recommendations
        
        # Check cache
        cache_key = f"personalized_recs_{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        recommendations = []
        
        # Collaborative filtering
        cf_recommendations = self.collaborative_filtering(user)
        recommendations.extend(cf_recommendations)
        
        # Content-based filtering
        cb_recommendations = self.content_based_filtering(user)
        recommendations.extend(cb_recommendations)
        
        # Popular products
        if len(recommendations) < limit:
            popular = self.get_popular_products(limit - len(recommendations))
            recommendations.extend(popular)
        
        # Remove duplicates
        recommendations = self.remove_duplicates(recommendations)[:limit]
        
        # Cache results
        cache.set(cache_key, recommendations, self.cache_timeout)
        
        return recommendations
    
    def collaborative_filtering(self, user, limit=10):
        """Collaborative filtering using user-item matrix"""
        try:
            # Get user interactions
            interactions = UserInteraction.objects.filter(
                interaction_type__in=['purchase', 'cart_add', 'view']
            ).values('user_id', 'product_id', 'interaction_type', 'weight')
            
            if not interactions:
                return []
            
            # Create user-item matrix
            df = pd.DataFrame(interactions)
            
            # Assign weights to different interaction types
            weight_map = {
                'purchase': 5.0,
                'cart_add': 3.0,
                'view': 1.0,
            }
            df['weight'] = df.apply(
                lambda x: x['weight'] * weight_map.get(x['interaction_type'], 1.0),
                axis=1
            )
            
            # Create pivot table
            user_item_matrix = df.pivot_table(
                index='user_id',
                columns='product_id',
                values='weight',
                aggfunc='sum',
                fill_value=0
            )
            
            # Calculate user similarity
            user_similarity = cosine_similarity(user_item_matrix)
            
            # Get current user index
            user_idx = user_item_matrix.index.get_loc(user.id)
            
            # Get similar users
            similar_users = np.argsort(user_similarity[user_idx])[-5:][::-1]
            
            # Get products from similar users
            recommended_products = []
            current_user_products = set(
                UserInteraction.objects.filter(user=user).values_list('product_id', flat=True)
            )
            
            for sim_user_idx in similar_users:
                sim_user_id = user_item_matrix.index[sim_user_idx]
                sim_user_products = user_item_matrix.iloc[sim_user_idx]
                
                # Get products with high interaction
                high_interaction = sim_user_products[sim_user_products > 2].sort_values(ascending=False)
                
                for product_id, score in high_interaction.items():
                    if product_id not in current_user_products:
                        recommended_products.append({
                            'product_id': product_id,
                            'score': float(score * user_similarity[user_idx][sim_user_idx]),
                            'type': 'collaborative'
                        })
            
            # Sort by score
            recommended_products.sort(key=lambda x: x['score'], reverse=True)
            
            # Get product objects
            product_ids = [item['product_id'] for item in recommended_products[:limit]]
            products = Product.objects.filter(id__in=product_ids, is_active=True)
            
            return list(products)
        
        except Exception as e:
            logger.error(f"Collaborative filtering failed: {e}")
            return []
    
    def content_based_filtering(self, user, limit=10):
        """Content-based filtering using product features"""
        try:
            # Get user's preferred products
            user_products = Product.objects.filter(
                interactions__user=user,
                interactions__interaction_type__in=['purchase', 'cart_add'],
                is_active=True
            ).distinct()[:10]
            
            if not user_products:
                return []
            
            # Get all products
            all_products = Product.objects.filter(is_active=True).exclude(
                id__in=user_products.values_list('id', flat=True)
            )
            
            # Create product features
            product_features = []
            for product in list(user_products) + list(all_products[:100]):
                features = self.extract_product_features(product)
                product_features.append(features)
            
            # Create TF-IDF matrix
            tfidf = TfidfVectorizer(max_features=1000)
            tfidf_matrix = tfidf.fit_transform(product_features)
            
            # Calculate similarity
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # Get recommendations based on user's products
            user_product_indices = list(range(len(user_products)))
            other_product_indices = list(range(len(user_products), len(product_features)))
            
            recommendations = []
            for user_idx in user_product_indices:
                for other_idx in other_product_indices:
                    similarity = similarity_matrix[user_idx][other_idx]
                    if similarity > 0.3:  # Threshold
                        recommendations.append({
                            'product': all_products[other_idx - len(user_products)],
                            'score': similarity,
                            'type': 'content_based'
                        })
            
            # Sort by score
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return [rec['product'] for rec in recommendations[:limit]]
        
        except Exception as e:
            logger.error(f"Content-based filtering failed: {e}")
            return []
    
    def extract_product_features(self, product):
        """Extract features for content-based filtering"""
        features = []
        
        # Add product name
        features.append(product.name)
        
        # Add category
        if product.category:
            features.append(product.category.name)
            if product.category.parent:
                features.append(product.category.parent.name)
        
        # Add brand
        if product.brand:
            features.append(product.brand.name)
        
        # Add tags
        features.extend(product.tags.names())
        
        # Add description
        features.append(product.short_description)
        
        return ' '.join(features)
    
    def get_similar_products(self, product, limit=10):
        """Get similar products"""
        # Check cache
        cache_key = f"similar_products_{product.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        similar_products = []
        
        # Get from pre-computed similarities
        similarities = ProductSimilarity.objects.filter(
            product1=product,
            similarity_score__gt=0.3
        ).order_by('-similarity_score')[:limit]
        
        if similarities:
            similar_products = [sim.product2 for sim in similarities]
        else:
            # Calculate on the fly
            similar_products = self.calculate_similar_products(product, limit)
        
        # Cache results
        cache.set(cache_key, similar_products, self.cache_timeout)
        
        return similar_products
    
    def calculate_similar_products(self, product, limit=10):
        """Calculate similar products based on features"""
        all_products = Product.objects.filter(is_active=True).exclude(id=product.id)
        
        # Extract features
        target_features = self.extract_product_features(product)
        other_features = [self.extract_product_features(p) for p in all_products]
        
        # Create TF-IDF matrix
        tfidf = TfidfVectorizer(max_features=1000)
        all_features = [target_features] + other_features
        tfidf_matrix = tfidf.fit_transform(all_features)
        
        # Calculate similarity
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        # Get top similar products
        top_indices = np.argsort(similarity_scores)[-limit:][::-1]
        
        similar_products = []
        for idx in top_indices:
            if similarity_scores[idx] > 0.3:
                product_obj = all_products[idx]
                similar_products.append(product_obj)
                
                # Save similarity for future use
                ProductSimilarity.objects.update_or_create(
                    product1=product,
                    product2=product_obj,
                    similarity_type='content',
                    defaults={'similarity_score': similarity_scores[idx]}
                )
        
        return similar_products
    
    def get_frequently_bought_together(self, product, limit=5):
        """Get frequently bought together products"""
        cache_key = f"frequently_bought_{product.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Find orders containing this product
        order_items = OrderItem.objects.filter(product=product)
        order_ids = order_items.values_list('order_id', flat=True)
        
        # Find other products in same orders
        related_items = OrderItem.objects.filter(
            order_id__in=order_ids
        ).exclude(product=product).values('product').annotate(
            count=Count('product')
        ).order_by('-count')[:limit]
        
        product_ids = [item['product'] for item in related_items]
        frequently_bought = Product.objects.filter(
            id__in=product_ids,
            is_active=True
        )
        
        cache.set(cache_key, frequently_bought, self.cache_timeout)
        
        return frequently_bought
    
    def get_trending_products(self, limit=10):
        """Get trending products"""
        cache_key = f"trending_{limit}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Based on recent interactions
        recent_interactions = UserInteraction.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).values('product').annotate(
            interaction_count=Count('product'),
            total_weight=Avg('weight')
        ).order_by('-interaction_count')[:limit]
        
        product_ids = [item['product'] for item in recent_interactions]
        trending = Product.objects.filter(id__in=product_ids, is_active=True)
        
        cache.set(cache_key, trending, self.cache_timeout)
        
        return trending
    
    def get_popular_products(self, limit=10):
        """Get popular products"""
        popular = Product.objects.filter(
            is_active=True,
            sales_count__gt=0
        ).order_by('-sales_count', '-views_count', '-average_rating')[:limit]
        
        return popular
    
    def remove_duplicates(self, products):
        """Remove duplicate products from list"""
        seen = set()
        unique_products = []
        
        for product in products:
            if product.id not in seen:
                seen.add(product.id)
                unique_products.append(product)
        
        return unique_products
    
    def update_user_embedding(self, user):
        """Update user embedding based on interactions"""
        try:
            # Get user interactions
            interactions = UserInteraction.objects.filter(user=user).select_related('product')
            
            if not interactions:
                return None
            
            # Create user profile vector
            product_features = []
            weights = []
            
            for interaction in interactions:
                features = self.extract_product_features(interaction.product)
                product_features.append(features)
                weights.append(interaction.weight)
            
            # Create TF-IDF matrix
            tfidf = TfidfVectorizer(max_features=128)
            tfidf_matrix = tfidf.fit_transform(product_features)
            
            # Weighted average of product vectors
            user_vector = np.average(
                tfidf_matrix.toarray(),
                axis=0,
                weights=weights
            )
            
            # Reduce dimensionality
            svd = TruncatedSVD(n_components=128)
            user_embedding = svd.fit_transform(user_vector.reshape(1, -1))[0]
            
            # Save embedding
            from .models import UserEmbedding
            UserEmbedding.objects.update_or_create(
                user=user,
                defaults={
                    'embedding': user_embedding.tolist(),
                    'dimension': 128
                }
            )
            
            return user_embedding
        
        except Exception as e:
            logger.error(f"Failed to update user embedding: {e}")
            return None