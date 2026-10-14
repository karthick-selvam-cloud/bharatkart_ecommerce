import hashlib
import pickle
import os
from django.conf import settings
import logging

try:
    import faiss
except ImportError:
    faiss = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except ImportError:
    chromadb = None

try:
    import numpy as np
except ImportError:
    np = None

logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for embeddings using FAISS and ChromaDB"""
    
    def __init__(self):
        self.model = None
        self.faiss_index = None
        self.chroma_client = None
        self.collection = None
        self.embedding_dim = 384  # Default for all-MiniLM-L6-v2
        self.metadata_list = []
        
    def load_model(self):
        """Load sentence transformer model"""
        if self.model is None:
            try:
                # Use lightweight model for production
                if SentenceTransformer is None:
                    raise ImportError('sentence-transformers is not installed')
                self.model = SentenceTransformer(
                    getattr(settings, 'SENTENCE_TRANSFORMER_MODEL', 'all-MiniLM-L6-v2')
                )
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info("Sentence transformer model loaded")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                # Fallback to even smaller model
                self.model = False
        return self.model
    
    def generate_embeddings(self, texts):
        """Generate embeddings for texts"""
        model = self.load_model()
        if model:
            return model.encode(
                texts,
                show_progress_bar=False,
                convert_to_numpy=True,
            )

        # Deterministic local fallback keeps search usable without ML downloads.
        vectors = []
        for text in texts:
            vector = [0.0] * self.embedding_dim
            for token in text.lower().split():
                digest = hashlib.sha256(token.encode('utf-8')).digest()
                index = int.from_bytes(digest[:4], 'big') % self.embedding_dim
                vector[index] += 1.0
            norm = sum(value * value for value in vector) ** 0.5
            vectors.append([value / norm for value in vector] if norm else vector)
        return vectors

    def _as_float32_matrix(self, embeddings):
        """Return embeddings in the matrix format required by FAISS."""
        if np is None:
            raise RuntimeError('NumPy is required for FAISS operations')
        return np.asarray(embeddings, dtype='float32')
    
    def init_faiss(self):
        """Initialize FAISS index"""
        if faiss is None:
            return None
        if self.faiss_index is None:
            self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
        return self.faiss_index

    def reset_faiss(self):
        """Clear the in-memory index before a full knowledge-base rebuild."""
        if self.faiss_index is not None:
            self.faiss_index.reset()
        self.metadata_list = []
    
    def init_chroma(self):
        """Initialize ChromaDB client"""
        if chromadb is None:
            raise RuntimeError('ChromaDB is not installed')
        if self.chroma_client is None:
            self.chroma_client = chromadb.Client(ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=os.path.join(settings.BASE_DIR, 'chroma_db')
            ))
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
        return self.chroma_client
    
    def add_to_faiss(self, texts, metadata_list=None):
        """Add texts to FAISS index"""
        embeddings = self.generate_embeddings(texts)
        index = self.init_faiss()
        if index is not None and len(texts) > 0:
            index.add(self._as_float32_matrix(embeddings))
        
        # Store metadata
        if metadata_list:
            self.metadata_list.extend(metadata_list)
        
        return embeddings
    
    def search_faiss(self, query, k=5):
        """Search FAISS index"""
        if self.faiss_index is None or self.faiss_index.ntotal == 0:
            return [], []
        k = min(k, self.faiss_index.ntotal)
        query_embedding = self.generate_embeddings([query])[0]
        distances, indices = self.faiss_index.search(
            self._as_float32_matrix([query_embedding]),
            k
        )
        return distances[0], indices[0]
    
    def add_to_chroma(self, texts, ids, metadata_list=None):
        """Add texts to ChromaDB"""
        embeddings = self.generate_embeddings(texts)
        
        self.init_chroma()
        self.collection.add(
            embeddings=embeddings.tolist() if hasattr(embeddings, 'tolist') else embeddings,
            documents=texts,
            ids=ids,
            metadatas=metadata_list or [{}] * len(texts)
        )
        
        return embeddings
    
    def search_chroma(self, query, k=5):
        """Search ChromaDB"""
        query_embedding = self.generate_embeddings([query])[0]
        
        self.init_chroma()
        results = self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
                if hasattr(query_embedding, 'tolist')
                else query_embedding
            ],
            n_results=k
        )
        
        return results
    
    def save_index(self, filepath):
        """Save FAISS index to disk"""
        if self.faiss_index is not None and faiss is not None:
            filepath = str(filepath)
            directory = os.path.dirname(filepath)
            if directory:
                os.makedirs(directory, exist_ok=True)
            faiss.write_index(self.faiss_index, filepath)
            
            # Save metadata
            metadata_filepath = filepath + '.metadata'
            with open(metadata_filepath, 'wb') as f:
                pickle.dump(self.metadata_list, f)
    
    def load_index(self, filepath):
        """Load FAISS index from disk"""
        filepath = str(filepath)
        if faiss is not None and os.path.exists(filepath):
            self.faiss_index = faiss.read_index(filepath)
            self.embedding_dim = self.faiss_index.d
            
            # Load metadata
            metadata_filepath = filepath + '.metadata'
            if os.path.exists(metadata_filepath):
                with open(metadata_filepath, 'rb') as f:
                    self.metadata_list = pickle.load(f)
            
            return True
        return False


class ElasticsearchVectorStore:
    """Elasticsearch-based vector store for production"""
    
    def __init__(self):
        from elasticsearch import Elasticsearch
        self.client = Elasticsearch(['http://localhost:9200'])
        self.index_name = 'knowledge_base'
    
    def create_index(self):
        """Create index with vector mapping"""
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "content": {"type": "text"},
                    "category": {"type": "keyword"},
                    "tags": {"type": "keyword"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 384,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name, body=mapping)
    
    def index_document(self, doc_id, title, content, category, tags, embedding):
        """Index document with embedding"""
        doc = {
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "embedding": embedding
        }
        
        self.client.index(index=self.index_name, id=doc_id, body=doc)
    
    def search(self, query_embedding, k=5):
        """Search for similar documents"""
        query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        }
        
        response = self.client.search(
            index=self.index_name,
            body={"query": query, "size": k}
        )
        
        return response['hits']['hits']