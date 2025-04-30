"""
Response Generator Module

This module handles the generation of responses to user queries based on
retrieved documents using a language model.
"""

import os
import re
from typing import Dict, List, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class ResponseGenerator:
    """Class for generating responses to user queries."""
    
    def __init__(self, model_name: str = "google/flan-t5-base"):
        """
        Initialize the response generator.
        
        Args:
            model_name: Name of the language model to use for response generation
        """
        self.model_name = model_name
        print(f"Loading model: {model_name}")
        
        # Load the generator model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.generator = pipeline(
            "text2text-generation", 
            model=model_name, 
            tokenizer=self.tokenizer,
            max_length=512
        )
    
    def format_documents_for_prompt(self, documents: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string for the prompt.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not documents:
            return "No relevant information found."
        
        # Sort documents by type and score
        sorted_docs = sorted(documents, key=lambda x: (-x["score"], x["type"]))
        
        context_parts = []
        
        for doc in sorted_docs:
            doc_type = doc["type"]
            metadata = doc["metadata"]
            
            if doc_type == "restaurant":
                context_parts.append(f"Restaurant Information - {metadata['name']}:")
                if metadata.get("address"):
                    context_parts.append(f"Address: {metadata['address']}, {metadata['city']}, {metadata['state']}")
                if metadata.get("hours"):
                    context_parts.append(f"Hours: {metadata['hours']}")
                if metadata.get("special_features"):
                    context_parts.append(f"Special Features: {metadata['special_features']}")
                if metadata.get("phone"):
                    context_parts.append(f"Contact: {metadata['phone']}")
                context_parts.append("")
            
            elif doc_type == "menu_item":
                context_parts.append(f"Menu Item - {metadata['restaurant']} - {metadata['name']}:")
                if metadata.get("price"):
                    context_parts.append(f"Price: {metadata['price']}")
                if metadata.get("description"):
                    context_parts.append(f"Description: {metadata['description']}")
                if metadata.get("section"):
                    context_parts.append(f"Section: {metadata['section']}")
                if metadata.get("dietary_info"):
                    context_parts.append(f"Dietary Info: {metadata['dietary_info']}")
                context_parts.append("")
        
        return "\n".join(context_parts)
    
    def create_prompt(self, query: str, documents: List[Dict[str, Any]], chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Create a prompt for the language model using the query and retrieved documents.
        
        Args:
            query: The user query
            documents: List of retrieved documents
            chat_history: Optional list of previous chat messages
            
        Returns:
            Formatted prompt string
        """
        # Format the documents into a context string
        context = self.format_documents_for_prompt(documents)
        
        # Include chat history if provided
        history_text = ""
        if chat_history and len(chat_history) > 0:
            history_parts = []
            for message in chat_history[-3:]:  # Only include the last 3 messages for brevity
                role = message.get("role", "").capitalize()
                content = message.get("content", "")
                history_parts.append(f"{role}: {content}")
            history_text = "\nPrevious Conversation:\n" + "\n".join(history_parts)
        
        # Create the full prompt
        prompt = f"""Based on the following information about restaurants and their menus, 
please answer the query accurately and helpfully.

Context Information:
{context}
{history_text}

Query: {query}

Answer:"""
        
        return prompt
    
    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the language model.
        
        Args:
            prompt: The prompt for the language model
            
        Returns:
            Generated response text
        """
        # Generate response using the model
        outputs = self.generator(prompt, max_length=512, num_return_sequences=1)
        response = outputs[0]["generated_text"]
        
        # Clean up the response
        response = self._clean_response(response)
        
        return response
    
    def _clean_response(self, response: str) -> str:
        """
        Clean up the generated response.
        
        Args:
            response: The raw generated response
            
        Returns:
            Cleaned response text
        """
        # Remove any prompt artifacts that might be in the response
        response = re.sub(r'^Answer:\s*', '', response)
        
        # Clean up any extra whitespace
        response = re.sub(r'\s+', ' ', response).strip()
        
        return response
    
    def answer_query(self, query: str, documents: List[Dict[str, Any]], chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Generate a response to a user query using retrieved documents.
        
        Args:
            query: The user query
            documents: List of retrieved documents
            chat_history: Optional list of previous chat messages
            
        Returns:
            Generated response text
        """
        # Create the prompt
        prompt = self.create_prompt(query, documents, chat_history)
        
        # Generate and return the response
        return self.generate_response(prompt)
    
    def handle_no_results(self, query: str) -> str:
        """
        Generate a response when no relevant documents are found.
        
        Args:
            query: The user query
            
        Returns:
            Fallback response text
        """
        fallback_prompt = f"""I don't have specific information about that in my restaurant database. 
However, I can try to give a general response.

Query: {query}

Answer:"""
        
        return self.generate_response(fallback_prompt)
    
    def generate_comparison(self, query: str, restaurant_docs: Dict[str, List[Dict[str, Any]]]) -> str:
        """
        Generate a comparison response between multiple restaurants.
        
        Args:
            query: The user query
            restaurant_docs: Dictionary mapping restaurant names to their documents
            
        Returns:
            Generated comparison text
        """
        # Format context with clearly separated restaurant information
        context_parts = ["Here is information about the restaurants you want to compare:"]
        
        for restaurant_name, docs in restaurant_docs.items():
            context_parts.append(f"\n--- {restaurant_name} ---")
            
            # Add restaurant general info
            restaurant_info = [doc for doc in docs if doc["type"] == "restaurant"]
            if restaurant_info:
                metadata = restaurant_info[0]["metadata"]
                if metadata.get("special_features"):
                    context_parts.append(f"Special Features: {metadata['special_features']}")
            
            # Add menu items info
            menu_items = [doc for doc in docs if doc["type"] == "menu_item"]
            if menu_items:
                context_parts.append("Menu Items:")
                for item in menu_items[:5]:  # Limit to 5 items for brevity
                    metadata = item["metadata"]
                    item_text = f"- {metadata['name']}"
                    if metadata.get("price"):
                        item_text += f" ({metadata['price']})"
                    if metadata.get("dietary_info"):
                        item_text += f" - {metadata['dietary_info']}"
                    context_parts.append(item_text)
        
        # Create the comparison prompt
        comparison_prompt = f"""Based on the following information about multiple restaurants,
please provide a comparison addressing this query.

{' '.join(context_parts)}

Query for comparison: {query}

Detailed comparison:"""
        
        # Generate and return the response
        return self.generate_response(comparison_prompt) 