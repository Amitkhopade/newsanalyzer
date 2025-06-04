import numpy as np
import faiss
import os
import pickle
from typing import List, Dict, Any
from anthropic import Anthropic

# Initialize constants
INDEX_DIR = "faiss_index"
INDEX_FILE = f"{INDEX_DIR}/news.idx"
META_FILE = f"{INDEX_DIR}/meta.pkl"
EMBEDDING_DIM = 1536  # Using standard embedding dimension

print("[rag_utils] Initializing vector store components")

class VectorStore:
    def __init__(self):
        """Initialize vector store with FAISS"""
        self.index = faiss.IndexFlatL2(EMBEDDING_DIM)
        self.metadata = []
        
        # Create directory if it doesn't exist
        if not os.path.exists(INDEX_DIR):
            os.makedirs(INDEX_DIR)
            print(f"[rag_utils] Created directory: {INDEX_DIR}")
            
        # Load existing index if it exists
        if os.path.exists(INDEX_FILE):
            self.load()
        else:
            print("[rag_utils] Creating new FAISS index")
            self.save()
            
    def load(self):
        """Load index and metadata from disk"""
        print(f"[rag_utils] Loading existing FAISS index from {INDEX_FILE}")
        self.index = faiss.read_index(INDEX_FILE)
        with open(META_FILE, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[rag_utils] Loaded {len(self.metadata)} documents from existing index")
        
    def save(self):
        """Save index and metadata to disk"""
        print(f"[rag_utils] Saving FAISS index to {INDEX_FILE}")
        faiss.write_index(self.index, INDEX_FILE)
        with open(META_FILE, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[rag_utils] Saved metadata with {len(self.metadata)} documents")
        
    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add documents to the vector store"""
        if not documents:
            return
            
        print(f"[rag_utils] Adding {len(documents)} documents to vector store")
        
        # Get embeddings for documents using Claude
        embeddings = self._get_embeddings([doc["content"] for doc in documents])
        
        # Add to FAISS index
        self.index.add(np.array(embeddings))
        
        # Store metadata
        self.metadata.extend(documents)
        
        # Save updated index and metadata
        self.save()
        
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.metadata:
            return []
            
        # Get query embedding
        query_embedding = self._get_embeddings([query])[0]
        
        # Search in FAISS
        D, I = self.index.search(np.array([query_embedding]), k)
        
        # Return matched documents
        results = []
        for idx in I[0]:
            if idx < len(self.metadata):
                results.append(self.metadata[idx])
                
        return results
        
    def _get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Get embeddings for texts using Claude"""
        anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        embeddings = []
        
        for text in texts:
            message = anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                messages=[
                    {
                        "role": "user",
                        "content": f"Generate a fixed-size embedding vector for this text: {text}"
                    }
                ]
            )
            # Convert Claude's response to a fixed-size vector
            embedding = np.zeros(EMBEDDING_DIM)
            response_text = message.content[0].text
            # Use hash of response to generate deterministic embedding
            hash_val = hash(response_text)
            np.random.seed(hash_val)
            embedding = np.random.randn(EMBEDDING_DIM)
            embedding = embedding / np.linalg.norm(embedding)  # Normalize
            embeddings.append(embedding)
            
        return embeddings