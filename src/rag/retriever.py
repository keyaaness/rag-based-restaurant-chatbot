"""
Document Retriever Module

This module handles the retrieval of relevant documents from the knowledge base
based on user queries using vector similarity search.
"""

import os
import json
import faiss
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer

class DocumentRetriever:
    """Class for retrieving documents from the knowledge base."""
    
    def __init__(self, knowledge_base_dir: str = "data/processed/kb"):
        """
        Initialize the document retriever.
        
        Args:
            knowledge_base_dir: Directory containing the knowledge base
        """
        self.kb_dir = Path(knowledge_base_dir)
        
        # Load model information
        model_info_path = self.kb_dir / "model_info.json"
        if not model_info_path.exists():
            raise FileNotFoundError(f"Model info file not found: {model_info_path}")
        
        with open(model_info_path, 'r', encoding='utf-8') as f:
            model_info = json.load(f)
        
        # Load the same model used to create the embeddings
        self.model_name = model_info["model_name"]
        print(f"Loading model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        
        # Load FAISS index
        index_path = self.kb_dir / "document_index.faiss"
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        self.index = faiss.read_index(str(index_path))
        
        # Load document metadata
        with open(self.kb_dir / "document_metadata.json", 'r', encoding='utf-8') as f:
            self.document_metadata = json.load(f)
        
        # Load document IDs
        with open(self.kb_dir / "document_ids.json", 'r', encoding='utf-8') as f:
            self.document_ids = json.load(f)
        
        # Load full documents
        with open(self.kb_dir / "documents.json", 'r', encoding='utf-8') as f:
            self.documents = json.load(f)
        
        print(f"Loaded {len(self.documents)} documents in the knowledge base")
    
    def query_to_embedding(self, query: str) -> np.ndarray:
        """
        Convert a text query to an embedding vector.
        
        Args:
            query: The user query
            
        Returns:
            Embedding vector for the query
        """
        # Encode the query text to an embedding vector
        query_embedding = self.model.encode([query])[0]
        
        # Reshape to match FAISS requirements
        query_embedding = np.array([query_embedding]).astype('float32')
        
        return query_embedding
    
    def retrieve_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant documents for a query.
        
        Args:
            query: The user query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata and scores
        """
        # Get query embedding
        query_embedding = self.query_to_embedding(query)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Extract the results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1:  # Valid index
                doc_id = self.document_ids[idx]
                metadata = self.document_metadata[doc_id]
                
                # Find the full document
                document = next((doc for doc in self.documents if doc["id"] == doc_id), None)
                
                if document:
                    results.append({
                        "id": doc_id,
                        "score": float(1.0 / (1.0 + distances[0][i])),  # Convert distance to a similarity score
                        "content": document["content"],
                        "metadata": metadata,
                        "type": document["type"]
                    })
        
        return results
    
    def search_by_restaurant(self, restaurant_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents related to a specific restaurant.
        
        Args:
            restaurant_name: Name of the restaurant
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata and scores
        """
        # Create a query focused on the restaurant
        query = f"Information about restaurant {restaurant_name}"
        
        # Get initial results
        results = self.retrieve_documents(query, top_k)
        
        # Filter for the specific restaurant
        results = [doc for doc in results if 
                  (doc["type"] == "restaurant" and doc["metadata"]["name"].lower() == restaurant_name.lower()) or
                  (doc["type"] == "menu_item" and doc["metadata"]["restaurant"].lower() == restaurant_name.lower())]
        
        return results
    
    def search_menu_items(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search specifically for menu items matching a query.
        
        Args:
            query: The user query about menu items
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant menu item documents with metadata and scores
        """
        # Create a menu-focused query
        menu_query = f"Menu item {query}"
        
        # Get initial results
        results = self.retrieve_documents(menu_query, top_k * 2)  # Get more results initially
        
        # Filter for menu items only
        menu_items = [doc for doc in results if doc["type"] == "menu_item"]
        
        # Return top_k menu items
        return menu_items[:top_k]
    
    def search_dietary_options(self, dietary_preference: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for menu items matching specific dietary preferences.
        
        Args:
            dietary_preference: The dietary preference (e.g., "vegetarian", "gluten-free")
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant menu item documents with metadata and scores
        """
        # Create a dietary-focused query
        dietary_query = f"Menu items with {dietary_preference} dietary preference"
        
        # Get initial results
        results = self.retrieve_documents(dietary_query, top_k * 3)  # Get more results initially
        
        # Filter for menu items with the dietary preference
        filtered_results = []
        for doc in results:
            if doc["type"] == "menu_item":
                if "dietary_info" in doc["metadata"] and dietary_preference.lower() in doc["metadata"]["dietary_info"].lower():
                    filtered_results.append(doc)
        
        # Return top_k filtered results
        return filtered_results[:top_k]
    
    def retrieve_with_fallback(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve documents with a fallback strategy for better results.
        
        Args:
            query: The user query
            top_k: Number of documents to retrieve
            
        Returns:
            List of relevant documents with metadata and scores
        """
        # Standard retrieval
        results = self.retrieve_documents(query, top_k)
        
        # If we got fewer results than requested, try a more general query
        if len(results) < top_k:
            # Extract key terms from the query (simplified approach)
            terms = query.lower().split()
            # Remove common words
            stopwords = {"the", "a", "an", "in", "on", "at", "of", "for", "with", "about", "restaurant", "food", "menu"}
            key_terms = [term for term in terms if term not in stopwords]
            
            if key_terms:
                # Create a simplified query
                simplified_query = " ".join(key_terms)
                additional_results = self.retrieve_documents(simplified_query, top_k - len(results))
                
                # Add only new results
                existing_ids = {doc["id"] for doc in results}
                for doc in additional_results:
                    if doc["id"] not in existing_ids:
                        results.append(doc)
        
        return results[:top_k] 