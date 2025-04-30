"""
Knowledge Base Builder

This script builds a knowledge base from processed restaurant data for efficient retrieval.
It creates embeddings for menu items, restaurant details, and other information to enable
semantic search with the RAG chatbot.
"""

import os
import sys
import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from tqdm import tqdm
import faiss
import pickle

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_base.data_processor import DataProcessor
from sentence_transformers import SentenceTransformer

class KnowledgeBaseBuilder:
    """Class for building a knowledge base from processed restaurant data."""
    
    def __init__(self, 
                 input_dir: str = "data/processed", 
                 output_dir: str = "data/processed/kb",
                 model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the knowledge base builder.
        
        Args:
            input_dir: Directory containing processed restaurant data
            output_dir: Directory where knowledge base will be saved
            model_name: Name of the sentence transformer model to use for embeddings
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.model_name = model_name
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load the sentence transformer model
        print(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
    
    def load_processed_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load processed restaurant data from CSV files.
        
        Returns:
            Tuple of (menu_items_df, restaurants_df)
        """
        # Load menu items data
        menu_items_path = self.input_dir / "menu_items.csv"
        if not menu_items_path.exists():
            raise FileNotFoundError(f"Menu items file not found: {menu_items_path}")
        menu_items_df = pd.read_csv(menu_items_path)
        
        # Load restaurants data
        restaurants_path = self.input_dir / "restaurants.csv"
        if not restaurants_path.exists():
            raise FileNotFoundError(f"Restaurants file not found: {restaurants_path}")
        restaurants_df = pd.read_csv(restaurants_path)
        
        return menu_items_df, restaurants_df
    
    def create_restaurant_documents(self, restaurants_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create document representations of restaurants for indexing.
        
        Args:
            restaurants_df: DataFrame containing restaurant information
            
        Returns:
            List of restaurant documents
        """
        documents = []
        
        for _, row in restaurants_df.iterrows():
            # Create a document for the restaurant
            restaurant_doc = {
                "type": "restaurant",
                "id": f"restaurant_{len(documents)}",
                "name": row["name"],
                "content": f"Restaurant: {row['name']}\nAddress: {row['address']}, {row['city']}, {row['state']}\nPhone: {row['phone']}\nEmail: {row['email']}\nHours: {row['hours']}\nSpecial Features: {row['special_features']}",
                "metadata": {
                    "name": row["name"],
                    "address": row["address"],
                    "city": row["city"],
                    "state": row["state"],
                    "phone": row["phone"],
                    "email": row["email"],
                    "hours": row["hours"],
                    "special_features": row["special_features"],
                    "url": row["url"]
                }
            }
            documents.append(restaurant_doc)
        
        return documents
    
    def create_menu_item_documents(self, menu_items_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Create document representations of menu items for indexing.
        
        Args:
            menu_items_df: DataFrame containing menu item information
            
        Returns:
            List of menu item documents
        """
        documents = []
        
        for _, row in menu_items_df.iterrows():
            # Create a document for the menu item
            menu_item_doc = {
                "type": "menu_item",
                "id": f"menu_item_{len(documents)}",
                "name": row["name"],
                "content": f"Restaurant: {row['restaurant']}\nMenu Item: {row['name']}\nPrice: {row['price']}\nDescription: {row['description']}\nSection: {row['section']}\nDietary Info: {row['dietary_info']}",
                "metadata": {
                    "restaurant": row["restaurant"],
                    "name": row["name"],
                    "price": row["price"],
                    "description": row["description"],
                    "section": row["section"],
                    "dietary_info": row["dietary_info"]
                }
            }
            documents.append(menu_item_doc)
        
        return documents
    
    def create_combined_documents(self, restaurant_docs: List[Dict[str, Any]], menu_item_docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine restaurant and menu item documents.
        
        Args:
            restaurant_docs: List of restaurant documents
            menu_item_docs: List of menu item documents
            
        Returns:
            Combined list of documents
        """
        return restaurant_docs + menu_item_docs
    
    def create_document_embeddings(self, documents: List[Dict[str, Any]]) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
        """
        Create embeddings for documents.
        
        Args:
            documents: List of documents
            
        Returns:
            Tuple of (embeddings_array, documents)
        """
        # Extract document content for embedding
        document_texts = [doc["content"] for doc in documents]
        
        # Create embeddings
        print(f"Creating embeddings for {len(document_texts)} documents...")
        embeddings = self.model.encode(document_texts, show_progress_bar=True)
        
        return embeddings, documents
    
    def build_faiss_index(self, embeddings: np.ndarray) -> faiss.IndexFlatL2:
        """
        Build a FAISS index for fast similarity search.
        
        Args:
            embeddings: Array of document embeddings
            
        Returns:
            FAISS index
        """
        # Get dimensions from embeddings
        d = embeddings.shape[1]
        
        # Create index
        index = faiss.IndexFlatL2(d)
        
        # Add vectors to index
        index.add(embeddings)
        
        return index
    
    def save_knowledge_base(self, index: faiss.Index, documents: List[Dict[str, Any]]) -> None:
        """
        Save the knowledge base components.
        
        Args:
            index: FAISS index
            documents: List of documents
        """
        # Save FAISS index
        faiss.write_index(index, str(self.output_dir / "document_index.faiss"))
        
        # Save documents
        with open(self.output_dir / "documents.json", 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        # Save document IDs for lookup
        document_ids = [doc["id"] for doc in documents]
        with open(self.output_dir / "document_ids.json", 'w', encoding='utf-8') as f:
            json.dump(document_ids, f, ensure_ascii=False)
        
        # Save metadata separately for quick access
        metadata = {doc["id"]: doc["metadata"] for doc in documents}
        with open(self.output_dir / "document_metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Save model name for reference
        with open(self.output_dir / "model_info.json", 'w', encoding='utf-8') as f:
            json.dump({"model_name": self.model_name}, f)
        
        print(f"Knowledge base saved to {self.output_dir}")
    
    def build_knowledge_base(self) -> None:
        """
        Build the knowledge base from processed data.
        """
        # Load processed data
        menu_items_df, restaurants_df = self.load_processed_data()
        
        print(f"Loaded {len(restaurants_df)} restaurants and {len(menu_items_df)} menu items")
        
        # Create document representations
        restaurant_docs = self.create_restaurant_documents(restaurants_df)
        menu_item_docs = self.create_menu_item_documents(menu_items_df)
        
        # Combine documents
        all_docs = self.create_combined_documents(restaurant_docs, menu_item_docs)
        
        # Create embeddings
        embeddings, all_docs = self.create_document_embeddings(all_docs)
        
        # Build FAISS index
        index = self.build_faiss_index(embeddings)
        
        # Save knowledge base
        self.save_knowledge_base(index, all_docs)
        
        print("Knowledge base built successfully")

def main():
    """
    Main function to build the knowledge base.
    """
    parser = argparse.ArgumentParser(description="Build a knowledge base from restaurant data.")
    parser.add_argument(
        "--input", 
        type=str, 
        default="data/processed",
        help="Directory containing processed restaurant data. Default is 'data/processed'."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="data/processed/kb",
        help="Directory to save knowledge base. Default is 'data/processed/kb'."
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="sentence-transformers/all-MiniLM-L6-v2",
        help="Name of the sentence transformer model to use for embeddings."
    )
    parser.add_argument(
        "--process", 
        action="store_true",
        help="Run data processing before building the knowledge base."
    )
    
    args = parser.parse_args()
    
    # Run data processing if requested
    if args.process:
        print("Processing raw restaurant data...")
        processor = DataProcessor(
            input_dir="data/raw",
            output_dir=args.input
        )
        processor.process_data()
    
    # Build knowledge base
    kb_builder = KnowledgeBaseBuilder(
        input_dir=args.input,
        output_dir=args.output,
        model_name=args.model
    )
    kb_builder.build_knowledge_base()

if __name__ == "__main__":
    main() 