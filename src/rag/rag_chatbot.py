"""
RAG Chatbot Module

This module implements a Retrieval Augmented Generation (RAG) chatbot
that answers user queries about restaurants using a knowledge base.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

from rag.retriever import DocumentRetriever
from rag.generator import ResponseGenerator

class RAGChatbot:
    """Class implementing a RAG-based restaurant chatbot."""
    
    def __init__(self, 
                 knowledge_base_dir: str = "data/processed/kb",
                 generator_model: str = "google/flan-t5-base"):
        """
        Initialize the RAG chatbot.
        
        Args:
            knowledge_base_dir: Directory containing the knowledge base
            generator_model: Name of the language model to use for response generation
        """
        # Initialize the retriever and generator components
        self.retriever = DocumentRetriever(knowledge_base_dir=knowledge_base_dir)
        self.generator = ResponseGenerator(model_name=generator_model)
        
        # Initialize chat history
        self.chat_history = []
    
    def add_message_to_history(self, role: str, content: str) -> None:
        """
        Add a message to the chat history.
        
        Args:
            role: Role of the message sender ("user" or "assistant")
            content: Content of the message
        """
        self.chat_history.append({
            "role": role,
            "content": content
        })
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """
        Get the chat history.
        
        Returns:
            List of chat history messages
        """
        return self.chat_history
    
    def clear_chat_history(self) -> None:
        """Clear the chat history."""
        self.chat_history = []
    
    def _detect_intent(self, query: str) -> Dict[str, Any]:
        """
        Detect the intent of the user query.
        
        Args:
            query: The user query
            
        Returns:
            Dictionary containing intent information
        """
        query_lower = query.lower()
        
        # Check for restaurant comparison intent
        if re.search(r'compare|comparison|versus|vs\.?|difference', query_lower):
            # Extract restaurant names (simplified approach)
            restaurant_names = []
            
            # Look for "between X and Y" pattern
            between_match = re.search(r'between\s+([a-zA-Z\s]+)\s+and\s+([a-zA-Z\s]+)', query_lower)
            if between_match:
                restaurant_names.append(between_match.group(1).strip())
                restaurant_names.append(between_match.group(2).strip())
            else:
                # Look for any restaurant names in the query based on known restaurants
                for doc in self.retriever.documents:
                    if doc["type"] == "restaurant":
                        restaurant_name = doc["metadata"]["name"].lower()
                        if restaurant_name in query_lower:
                            restaurant_names.append(doc["metadata"]["name"])
            
            if len(restaurant_names) >= 2:
                return {
                    "type": "comparison",
                    "restaurants": restaurant_names
                }
        
        # Check for dietary restriction intent
        dietary_terms = ["vegetarian", "vegan", "gluten-free", "gluten free", "nut-free", "dairy-free"]
        for term in dietary_terms:
            if term in query_lower:
                return {
                    "type": "dietary",
                    "preference": term
                }
        
        # Check for menu item intent
        if re.search(r'menu|item|dish|food|appetizer|entree|dessert', query_lower):
            return {
                "type": "menu_item",
                "query": query
            }
        
        # Check for restaurant-specific intent
        if re.search(r'restaurant|location|address|hour|contact', query_lower):
            for doc in self.retriever.documents:
                if doc["type"] == "restaurant":
                    restaurant_name = doc["metadata"]["name"].lower()
                    if restaurant_name in query_lower:
                        return {
                            "type": "restaurant_info",
                            "restaurant": doc["metadata"]["name"]
                        }
        
        # Default to generic query intent
        return {
            "type": "generic",
            "query": query
        }
    
    def answer(self, query: str) -> str:
        """
        Answer a user query using RAG.
        
        Args:
            query: The user query
            
        Returns:
            Generated response text
        """
        # Add user message to chat history
        self.add_message_to_history("user", query)
        
        # Detect intent
        intent = self._detect_intent(query)
        intent_type = intent["type"]
        
        documents = []
        
        # Retrieve relevant documents based on intent
        if intent_type == "comparison":
            restaurant_docs = {}
            for restaurant in intent["restaurants"]:
                restaurant_docs[restaurant] = self.retriever.search_by_restaurant(restaurant)
            
            # Generate comparison response
            response = self.generator.generate_comparison(query, restaurant_docs)
        
        elif intent_type == "dietary":
            documents = self.retriever.search_dietary_options(intent["preference"])
            if documents:
                response = self.generator.answer_query(query, documents, self.chat_history)
            else:
                response = f"I couldn't find any menu items with {intent['preference']} dietary preference in our database."
        
        elif intent_type == "menu_item":
            documents = self.retriever.search_menu_items(query)
            if documents:
                response = self.generator.answer_query(query, documents, self.chat_history)
            else:
                documents = self.retriever.retrieve_with_fallback(query)
                response = self.generator.answer_query(query, documents, self.chat_history)
        
        elif intent_type == "restaurant_info":
            documents = self.retriever.search_by_restaurant(intent["restaurant"])
            if documents:
                response = self.generator.answer_query(query, documents, self.chat_history)
            else:
                response = f"I couldn't find information about {intent['restaurant']} in our database."
        
        else:  # Generic query
            documents = self.retriever.retrieve_with_fallback(query)
            if documents:
                response = self.generator.answer_query(query, documents, self.chat_history)
            else:
                response = self.generator.handle_no_results(query)
        
        # Add assistant response to chat history
        self.add_message_to_history("assistant", response)
        
        return response 