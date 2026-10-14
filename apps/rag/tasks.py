from celery import shared_task
from django.core.cache import cache
from .rag_pipeline import HybridRAGPipeline
from apps.recommendations.recommendation_engine import RecommendationEngine
import logging

logger = logging.getLogger(__name__)

@shared_task
def reindex_knowledge_base_task():
    """Reindex knowledge base periodically"""
    try:
        pipeline = HybridRAGPipeline()
        pipeline.bulk_index_knowledge_base()
        logger.info("Knowledge base reindexed successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to reindex knowledge base: {e}")
        return False

@shared_task
def update_recommendations_task():
    """Update recommendations periodically"""
    try:
        engine = RecommendationEngine()
        
        # Update all active products
        from apps.products.models import Product
        products = Product.objects.filter(is_active=True)
        
        for product in products[:100]:  # Limit to prevent overload
            engine.get_similar_products(product)
        
        # Clear recommendation cache
        cache.clear()
        
        logger.info("Recommendations updated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to update recommendations: {e}")
        return False

@shared_task
def cleanup_old_queries_task():
    """Clean up old RAG queries"""
    from django.utils import timezone
    from .models import RAGQuery
    from datetime import timedelta
    
    # Delete queries older than 30 days
    cutoff = timezone.now() - timedelta(days=30)
    deleted_count = RAGQuery.objects.filter(created_at__lt=cutoff).delete()[0]
    
    logger.info(f"Cleaned up {deleted_count} old queries")
    return deleted_count