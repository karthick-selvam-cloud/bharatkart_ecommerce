import logging
import time
import hashlib
from typing import List, Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache
from .models import KnowledgeBase, DocumentChunk, VectorEmbedding, RAGQuery
from .vector_store import VectorStore
try:
    import openai
except ImportError:
    openai = None
try:
    from langchain.llms import OpenAI
except ImportError:
    OpenAI = None
try:
    import nltk
    from nltk.tokenize import sent_tokenize
except ImportError:
    nltk = None
    def sent_tokenize(text):
        return [part.strip() for part in text.replace('!', '.').replace('?', '.').split('.') if part.strip()]

logger = logging.getLogger(__name__)

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for customer support"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.cache_timeout = 3600  # 1 hour cache
        self.max_context_length = 2000
        self.similarity_threshold = 0.7
        self.index_path = getattr(
            settings,
            'FAISS_INDEX_PATH',
            settings.BASE_DIR / 'faiss_index' / 'knowledge_base.index',
        )
        self.vector_store.load_index(self.index_path)
        
        # Initialize OpenAI if API key is available
        if settings.OPENAI_API_KEY and openai and OpenAI:
            openai.api_key = settings.OPENAI_API_KEY
            self.llm = OpenAI(
                temperature=0.7,
                max_tokens=500,
                model="gpt-3.5-turbo"
            )
        else:
            self.llm = None
        
        # Download NLTK data if not present
        try:
            if nltk is None:
                raise LookupError
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            if nltk is None:
                return
            nltk.download('punkt', quiet=True)
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess the query"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = ' '.join(query.split())
        
        # Add query expansion
        query = self.expand_query(query)
        
        return query
    
    def expand_query(self, query: str) -> str:
        """Expand query with synonyms and related terms"""
        # Common e-commerce synonyms
        synonym_map = {
            'refund': 'refund return money back',
            'return': 'return refund exchange',
            'delivery': 'delivery shipping courier',
            'payment': 'payment pay transaction',
            'order': 'order purchase buy',
            'cancel': 'cancel cancellation remove',
            'track': 'track tracking status',
            'damaged': 'damaged broken defective',
        }
        
        words = query.split()
        expanded_words = []
        
        for word in words:
            expanded_words.append(word)
            if word in synonym_map:
                expanded_words.extend(synonym_map[word].split())
        
        return ' '.join(expanded_words)
    
    def retrieve_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents using vector similarity"""
        # Check cache first
        cache_key = (
            "rag_retrieval_"
            + hashlib.sha256(query.encode('utf-8')).hexdigest()
        )
        cached_results = cache.get(cache_key)
        if cached_results:
            return cached_results
        
        # Search in vector store
        results = []
        
        # Try FAISS search
        try:
            distances, indices = self.vector_store.search_faiss(query, k=k)
            
            for i, (distance, idx) in enumerate(zip(distances, indices)):
                if idx < len(self.vector_store.metadata_list):
                    metadata = self.vector_store.metadata_list[idx]
                    similarity_score = 1 / (1 + distance)  # Convert distance to similarity
                    
                    if similarity_score >= self.similarity_threshold:
                        results.append({
                            'content': metadata.get('content', ''),
                            'title': metadata.get('title', ''),
                            'category': metadata.get('category', ''),
                            'similarity_score': similarity_score,
                            'source_id': metadata.get('source_id'),
                        })
        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
        
        # Fallback to database search
        if not results:
            results = self.db_search(query, k)
        
        # Cache results
        cache.set(cache_key, results, self.cache_timeout)
        
        return results
    
    def db_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Fallback to database search"""
        from django.db.models import Q
        
        # Simple keyword search
        keywords = query.split()
        q_objects = Q()
        for keyword in keywords:
            q_objects |= Q(title__icontains=keyword) | Q(content__icontains=keyword)
        
        kb_articles = KnowledgeBase.objects.filter(
            q_objects,
            is_active=True
        )[:k]
        
        results = []
        for article in kb_articles:
            results.append({
                'content': article.content,
                'title': article.title,
                'category': article.category,
                'similarity_score': 0.5,  # Default score for DB search
                'source_id': article.id,
            })
        
        return results
    
    def generate_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using LLM or template-based approach"""
        
        if self.llm:
            # Use OpenAI for response generation
            return self.generate_with_openai(query, context)
        else:
            # Template-based response
            return self.generate_template_response(query, context)
    
    def generate_with_openai(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate response using OpenAI"""
        try:
            # Prepare context
            context_text = "\n\n".join([
                f"Title: {item['title']}\nContent: {item['content']}"
                for item in context[:3]
            ])
            
            # Truncate context if too long
            if len(context_text) > self.max_context_length:
                context_text = context_text[:self.max_context_length]
            
            prompt = f"""You are a helpful customer support assistant for BharatKart, an Indian e-commerce platform.
            
            User Question: {query}
            
            Relevant Information:
            {context_text}
            
            Please provide a helpful and accurate response based on the information above. 
            If the information is not sufficient, say so and suggest contacting human support.
            
            Response:"""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful customer support assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return self.generate_template_response(query, context)
    
    def generate_template_response(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Generate template-based response"""
        if not context:
            return self.get_fallback_response()
        
        # Use the most relevant document
        best_match = context[0]
        
        # Create response template
        response = f"Based on our knowledge base:\n\n{best_match['content']}"
        
        # Add source reference
        if best_match.get('source_id'):
            response += f"\n\nFor more information, please visit our help center or contact support."
        
        return response
    
    def get_fallback_response(self) -> str:
        """Get fallback response when no relevant documents found"""
        return (
            "I apologize, but I couldn't find specific information about your query. "
            "Here are some options:\n"
            "1. Please rephrase your question\n"
            "2. Contact our human support team for assistance\n"
            "3. Visit our Help Center for more information"
        )
    
    def process_query(self, query: str, user=None, session_id: str = None) -> Dict[str, Any]:
        """Main RAG pipeline method"""
        start_time = time.time()
        
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Retrieve relevant documents
        context = self.retrieve_documents(processed_query)
        
        # Generate response
        response = self.generate_response(query, context)
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Store query for analysis
        rag_query = RAGQuery.objects.create(
            user=user,
            query=query,
            response=response,
            context_chunks=[item['content'][:200] for item in context],
            similarity_scores=[item['similarity_score'] for item in context],
            response_time=response_time,
            status='success' if context else 'fallback'
        )
        
        return {
            'query': query,
            'response': response,
            'context': context,
            'response_time': response_time,
            'query_id': rag_query.uid,
            'status': 'success' if context else 'fallback',
        }
    
    def bulk_index_knowledge_base(self):
        """Index all knowledge base articles"""
        articles = KnowledgeBase.objects.filter(is_active=True)
        self.vector_store.reset_faiss()
        
        texts = []
        metadata_list = []
        
        for article in articles:
            # Split into chunks
            chunks = self.chunk_text(article.content)
            chunk_indexes = set(range(len(chunks)))
            if chunk_indexes:
                article.chunks.exclude(chunk_index__in=chunk_indexes).delete()
            else:
                article.chunks.all().delete()
            
            for i, chunk in enumerate(chunks):
                texts.append(f"{article.title}\n{chunk}")
                metadata_list.append({
                    'title': article.title,
                    'content': chunk,
                    'category': article.category,
                    'source_id': article.id,
                })
                
                # Save chunk to database
                DocumentChunk.objects.update_or_create(
                    knowledge_base=article,
                    chunk_index=i,
                    defaults={
                        'content': chunk,
                        'token_count': len(chunk.split()),
                    },
                )
        
        # Add to vector store
        if texts:
            self.vector_store.add_to_faiss(texts, metadata_list)
        self.vector_store.save_index(self.index_path)
        logger.info(f"Indexed {len(texts)} chunks from {len(articles)} articles")
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into chunks"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                
                # Keep overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                current_chunk = overlap_sentences
                current_length = sum(len(s) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks


class HybridRAGPipeline(RAGPipeline):
    """Hybrid RAG with semantic + keyword search"""
    
    def __init__(self):
        super().__init__()
        self.bm25_index = None
    
    def retrieve_documents(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve using hybrid approach"""
        # Semantic search
        semantic_results = super().retrieve_documents(query, k)
        
        # Keyword search (BM25)
        keyword_results = self.keyword_search(query, k)
        
        # Combine results
        combined_results = self.combine_results(semantic_results, keyword_results)
        
        return combined_results[:k]
    
    def keyword_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Keyword-based search using BM25"""
        # Get all documents
        documents = KnowledgeBase.objects.filter(is_active=True)
        corpus = [doc.get_embedding_text() for doc in documents]
        
        # Tokenize
        tokenized_corpus = [doc.lower().split() for doc in corpus]
        tokenized_query = query.lower().split()
        
        try:
            from rank_bm25 import BM25Okapi
            scores = BM25Okapi(tokenized_corpus).get_scores(tokenized_query)
        except ImportError:
            # Small dependency-free fallback for development and CI.
            scores = [
                sum(token in tokens for token in tokenized_query)
                for tokens in tokenized_corpus
            ]
        top_indices = [
            index for index, _ in sorted(
                enumerate(scores), key=lambda item: item[1], reverse=True
            )[:k]
        ]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = documents[idx]
                results.append({
                    'content': doc.content,
                    'title': doc.title,
                    'category': doc.category,
                    'similarity_score': float(scores[idx] / max(scores)) if max(scores) else 0,
                    'source_id': doc.id,
                })
        
        return results
    
    def combine_results(self, semantic_results, keyword_results):
        """Combine semantic and keyword search results"""
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            key = result.get('source_id')
            if key:
                combined[key] = result
                combined[key]['semantic_score'] = result['similarity_score']
                combined[key]['keyword_score'] = 0
        
        # Add keyword results
        for result in keyword_results:
            key = result.get('source_id')
            if key:
                if key in combined:
                    combined[key]['keyword_score'] = result['similarity_score']
                    # Hybrid score
                    combined[key]['similarity_score'] = (
                        0.6 * combined[key].get('semantic_score', 0) +
                        0.4 * result['similarity_score']
                    )
                else:
                    combined[key] = result
                    combined[key]['semantic_score'] = 0
                    combined[key]['keyword_score'] = result['similarity_score']
        
        # Sort by combined score
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x['similarity_score'],
            reverse=True
        )
        
        return sorted_results