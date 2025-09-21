import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer

class VectorDatabase:
    """
    FAISS-based vector database for efficient similarity search.
    Replaces pickle-based storage with scalable vector indexing.
    """
    
    def __init__(self, model_name: str = "multi-qa-MPNet-base-dot-v1", dimension: int = None):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
        # Get actual dimension from model
        if dimension is None:
            # Get dimension by encoding a test sentence
            test_embedding = self.model.encode(["test"], normalize_embeddings=True)
            self.dimension = test_embedding.shape[1]
        else:
            self.dimension = dimension
        
        # FAISS index for vectors
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner product (cosine similarity)
        
        # Metadata storage
        self.metadata = []
        self.texts = []
        
        # Paths
        self.index_path = "embeddings/faiss_index.bin"
        self.metadata_path = "embeddings/metadata.pkl"
        
    def add_embeddings(self, chunks: List[Dict]) -> None:
        """
        Add new chunks to the vector database.
        
        Args:
            chunks: List of chunk dictionaries with 'text' and optional 'metadata'
        """
        if not chunks:
            return
            
        print(f"🔹 Generating embeddings for {len(chunks)} chunks...")
        
        # Extract texts and generate embeddings
        texts = [chunk.get("text", "") for chunk in chunks]
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text.strip()]
        if not valid_texts:
            print("⚠️ No valid texts found in chunks")
            return
            
        try:
            vectors = self.model.encode(valid_texts, normalize_embeddings=True, show_progress_bar=True)
            
            # Add to FAISS index
            self.index.add(vectors.astype('float32'))
        except Exception as e:
            print(f"❌ Error generating embeddings: {e}")
            return
        
        # Store metadata (only for valid texts)
        valid_chunks = [chunk for chunk in chunks if chunk.get("text", "").strip()]
        for i, chunk in enumerate(valid_chunks):
            self.metadata.append({
                "text": chunk.get("text", ""),
                "metadata": chunk.get("metadata", {}),
                "doc_id": chunk.get("doc_id", ""),
                "chunk_id": chunk.get("chunk_id", f"chunk_{len(self.metadata)}")
            })
            self.texts.append(chunk.get("text", ""))
        
        print(f"✅ Added {len(valid_chunks)} embeddings to vector database")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar chunks using cosine similarity.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of (text, similarity_score, metadata) tuples
        """
        if self.index.ntotal == 0:
            return []
        
        # Encode query
        query_vector = self.model.encode([query], normalize_embeddings=True)
        
        # Search FAISS index
        scores, indices = self.index.search(query_vector.astype('float32'), top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid index
                results.append((
                    self.texts[idx],
                    float(score),
                    self.metadata[idx]
                ))
        
        return results
    
    def save(self) -> None:
        """Save the vector database to disk."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Save FAISS index
        faiss.write_index(self.index, self.index_path)
        
        # Save metadata
        with open(self.metadata_path, "wb") as f:
            pickle.dump({
                "metadata": self.metadata,
                "texts": self.texts,
                "model_name": self.model_name,
                "dimension": self.dimension
            }, f)
        
        print(f"💾 Saved vector database: {self.index.ntotal} vectors")
    
    def load(self) -> bool:
        """
        Load the vector database from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
            print("📁 No existing vector database found")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load metadata
            with open(self.metadata_path, "rb") as f:
                data = pickle.load(f)
                self.metadata = data["metadata"]
                self.texts = data["texts"]
                self.model_name = data.get("model_name", self.model_name)
                self.dimension = data.get("dimension", self.dimension)
            
            print(f"📂 Loaded vector database: {self.index.ntotal} vectors")
            return True
            
        except Exception as e:
            print(f"❌ Error loading vector database: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "model_name": f"{self.model_name} + Enhanced AI (Pegasus/RoBERTa/DialoGPT)",
            "index_path": self.index_path,
            "metadata_path": self.metadata_path
        }
    
    def clear(self) -> None:
        """Clear all data from the database."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata = []
        self.texts = []
        print("🗑️ Cleared vector database")

def migrate_from_pickle(pickle_path: str = "embeddings/embeddings.pkl") -> VectorDatabase:
    """
    Migrate existing pickle-based embeddings to FAISS vector database.
    
    Args:
        pickle_path: Path to existing pickle file
        
    Returns:
        VectorDatabase instance with migrated data
    """
    print("🔄 Migrating from pickle to FAISS...")
    
    # Load existing embeddings
    if not os.path.exists(pickle_path):
        print(f"❌ Pickle file not found: {pickle_path}")
        return VectorDatabase()
    
    with open(pickle_path, "rb") as f:
        embeddings = pickle.load(f)
    
    print(f"📂 Found {len(embeddings)} existing embeddings")
    
    # Create new vector database
    vector_db = VectorDatabase()
    
    # Convert format and add to FAISS
    chunks = []
    for emb in embeddings:
        chunks.append({
            "text": emb.get("text", ""),
            "metadata": emb.get("metadata", {}),
            "doc_id": emb.get("metadata", {}).get("doc_id", ""),
            "chunk_id": emb.get("metadata", {}).get("chunk_id", "")
        })
    
    vector_db.add_embeddings(chunks)
    vector_db.save()
    
    print("✅ Migration completed successfully!")
    return vector_db

if __name__ == "__main__":
    # Test the vector database
    print("🧪 Testing Vector Database...")
    
    # Try to migrate existing data
    vector_db = migrate_from_pickle()
    
    if vector_db.index.ntotal > 0:
        # Test search
        test_query = "resume experience"
        results = vector_db.search(test_query, top_k=3)
        
        print(f"\n🔍 Test search for: '{test_query}'")
        for i, (text, score, metadata) in enumerate(results):
            print(f"{i+1}. Score: {score:.4f}")
            print(f"   Text: {text[:100]}...")
            print(f"   Metadata: {metadata}")
            print()
    else:
        print("📝 No data found. Add some documents first using ingest.py")
