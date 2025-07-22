#!/usr/bin/env python3
"""
Image Vector Store for caching generated images based on prompts/tags
Uses OpenAI embeddings and local vector storage to optimize image generation costs
"""

import os
import json
import uuid
import hashlib
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import numpy as np
from datetime import datetime

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
except ImportError:
    print("Warning: LangChain imports failed. Install with: pip install langchain langchain-openai langchain-community faiss-cpu")
    OpenAIEmbeddings = None
    FAISS = None
    Document = None

from ..core.config import Config

class ImageVectorStore:
    """Vector store for caching generated images based on semantic similarity"""
    
    def __init__(self, store_path: Optional[str] = None):
        """Initialize the image vector store"""
        self.store_path = store_path or str(Path(__file__).parent.parent.parent / "image_cache")
        self.vector_store_path = Path(self.store_path) / "vector_store"
        self.metadata_path = Path(self.store_path) / "image_metadata.json"
        
        # Create directories
        Path(self.store_path).mkdir(exist_ok=True)
        self.vector_store_path.mkdir(exist_ok=True)
        
        # Initialize embeddings
        if OpenAIEmbeddings:
            self.embeddings = OpenAIEmbeddings(
                openai_api_base="https://litellm.tecosys.ai/",
                openai_api_key="sk-LLPrAbLPEaAJIduZjOyRzw",
                model="text-embedding-3-large"
            )
        else:
            self.embeddings = None
            print("Warning: OpenAI embeddings not available")
        
        # Load or initialize vector store
        self.vector_store = self._load_or_create_vector_store()
        
        # Load metadata
        self.metadata = self._load_metadata()
    
    def _load_or_create_vector_store(self):
        """Load existing vector store or create new one"""
        if not self.embeddings or not FAISS:
            return None
            
        vector_store_file = self.vector_store_path / "index.faiss"
        
        if vector_store_file.exists():
            try:
                # Load existing vector store
                vector_store = FAISS.load_local(
                    str(self.vector_store_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"✅ Loaded existing vector store with {vector_store.index.ntotal} images")
                return vector_store
            except Exception as e:
                print(f"Warning: Could not load existing vector store: {e}")
        
        # Create new empty vector store
        try:
            # Create with dummy document to initialize
            dummy_doc = Document(page_content="dummy", metadata={"image_id": "dummy"})
            vector_store = FAISS.from_documents([dummy_doc], self.embeddings)
            print("✅ Created new vector store")
            return vector_store
        except Exception as e:
            print(f"Warning: Could not create vector store: {e}")
            return None
    
    def _load_metadata(self) -> Dict:
        """Load image metadata from JSON file"""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
        
        return {}
    
    def _save_metadata(self):
        """Save image metadata to JSON file"""
        try:
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def _save_vector_store(self):
        """Save vector store to disk"""
        if self.vector_store:
            try:
                self.vector_store.save_local(str(self.vector_store_path))
            except Exception as e:
                print(f"Warning: Could not save vector store: {e}")
    
    def _generate_image_id(self, prompt: str, tags: List[str]) -> str:
        """Generate unique image ID based on prompt and tags"""
        content = f"{prompt}_{','.join(sorted(tags))}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def search_similar_images(self, prompt: str, tags: List[str] = None, similarity_threshold: float = 0.85, top_k: int = 3) -> List[Dict]:
        """Search for similar images based on prompt and tags"""
        if not self.vector_store or not self.embeddings:
            return []
        
        tags = tags or []
        search_text = f"{prompt} {' '.join(tags)}"
        
        try:
            # Search for similar documents
            results = self.vector_store.similarity_search_with_score(search_text, k=top_k)
            
            similar_images = []
            for doc, score in results:
                # Convert distance to similarity (FAISS returns distance, lower is better)
                similarity = 1.0 / (1.0 + score)
                
                if similarity >= similarity_threshold:
                    image_id = doc.metadata.get('image_id')
                    if image_id in self.metadata and image_id != "dummy":
                        image_info = self.metadata[image_id].copy()
                        image_info['similarity'] = similarity
                        image_info['image_id'] = image_id
                        similar_images.append(image_info)
            
            return sorted(similar_images, key=lambda x: x['similarity'], reverse=True)
            
        except Exception as e:
            print(f"Warning: Search failed: {e}")
            return []
    
    def add_image(self, prompt: str, image_path: str, tags: List[str] = None, story_type: str = None, additional_metadata: Dict = None) -> str:
        """Add a new image to the vector store"""
        tags = tags or []
        additional_metadata = additional_metadata or {}
        
        # Generate unique image ID
        image_id = self._generate_image_id(prompt, tags)
        
        # If image already exists, update metadata
        if image_id in self.metadata:
            print(f"Image already exists: {image_id}")
            return image_id
        
        # Prepare document for vector store
        search_text = f"{prompt} {' '.join(tags)}"
        
        # Store metadata
        self.metadata[image_id] = {
            "prompt": prompt,
            "image_path": image_path,
            "tags": tags,
            "story_type": story_type,
            "created_at": datetime.now().isoformat(),
            "usage_count": 1,
            **additional_metadata
        }
        
        # Add to vector store
        if self.vector_store and self.embeddings:
            try:
                doc = Document(
                    page_content=search_text,
                    metadata={"image_id": image_id}
                )
                
                # Add document to vector store
                self.vector_store.add_documents([doc])
                
                # Save everything
                self._save_vector_store()
                self._save_metadata()
                
                print(f"✅ Added image to vector store: {image_id}")
                return image_id
                
            except Exception as e:
                print(f"Warning: Could not add to vector store: {e}")
        
        # Fallback: just save metadata
        self._save_metadata()
        return image_id
    
    def get_image_info(self, image_id: str) -> Optional[Dict]:
        """Get image information by ID"""
        return self.metadata.get(image_id)
    
    def increment_usage(self, image_id: str):
        """Increment usage count for an image"""
        if image_id in self.metadata:
            self.metadata[image_id]["usage_count"] = self.metadata[image_id].get("usage_count", 0) + 1
            self.metadata[image_id]["last_used"] = datetime.now().isoformat()
            self._save_metadata()
    
    def find_or_generate_image(self, prompt: str, tags: List[str] = None, story_type: str = None, 
                              similarity_threshold: float = 0.85) -> Tuple[str, bool]:
        """
        Find existing similar image or indicate that generation is needed
        Returns: (image_path_or_id, is_existing)
        """
        tags = tags or []
        
        # Search for similar images
        similar_images = self.search_similar_images(prompt, tags, similarity_threshold)
        
        if similar_images:
            # Use the most similar existing image
            best_match = similar_images[0]
            image_id = best_match['image_id']
            
            # Increment usage count
            self.increment_usage(image_id)
            
            print(f"✅ Using existing image: {image_id} (similarity: {best_match['similarity']:.3f})")
            return best_match['image_path'], True
        
        # No similar image found, return unique filename for generation
        unique_id = str(uuid.uuid4())[:8]
        safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prompt = safe_prompt.replace(' ', '_')
        
        new_filename = f"{story_type or 'story'}_{safe_prompt}_{unique_id}"
        
        print(f"🔄 No similar image found, will generate: {new_filename}")
        return new_filename, False
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_images = len([k for k in self.metadata.keys() if k != "dummy"])
        total_usage = sum(img.get("usage_count", 0) for img in self.metadata.values())
        
        return {
            "total_images": total_images,
            "total_usage": total_usage,
            "cache_hits": total_usage - total_images,
            "cache_hit_rate": (total_usage - total_images) / max(total_usage, 1),
            "vector_store_size": self.vector_store.index.ntotal if self.vector_store else 0
        }
    
    def cleanup_unused_images(self, min_usage_count: int = 1, days_old: int = 30):
        """Remove images that haven't been used much or are old"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        to_remove = []
        
        for image_id, metadata in self.metadata.items():
            if image_id == "dummy":
                continue
                
            usage_count = metadata.get("usage_count", 0)
            created_at = datetime.fromisoformat(metadata.get("created_at", "1970-01-01"))
            
            if usage_count < min_usage_count and created_at < cutoff_date:
                to_remove.append(image_id)
        
        # Remove from metadata
        for image_id in to_remove:
            del self.metadata[image_id]
        
        self._save_metadata()
        print(f"🧹 Cleaned up {len(to_remove)} unused images")
        
        # Note: For vector store cleanup, you'd need to rebuild it
        # This is a limitation of FAISS - you can't easily remove specific documents
        
        return len(to_remove)

# Global instance for easy access
image_cache = ImageVectorStore()

def get_image_cache() -> ImageVectorStore:
    """Get the global image cache instance"""
    return image_cache
