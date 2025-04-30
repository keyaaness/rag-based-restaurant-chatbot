"""
Utility Module

This module provides utility functions for the restaurant chatbot application.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

def ensure_directory_exists(directory_path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
    """
    os.makedirs(directory_path, exist_ok=True)

def save_json(data: Any, file_path: str) -> None:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the output file
    """
    # Ensure the directory exists
    directory = os.path.dirname(file_path)
    ensure_directory_exists(directory)
    
    # Save the data
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_json(file_path: str) -> Any:
    """
    Load data from a JSON file.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        The loaded data
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_restaurant_names(knowledge_base_dir: str = "data/processed/kb") -> List[str]:
    """
    Get a list of all restaurant names in the knowledge base.
    
    Args:
        knowledge_base_dir: Directory containing the knowledge base
        
    Returns:
        List of restaurant names
    """
    kb_dir = Path(knowledge_base_dir)
    
    # Load the documents
    documents_path = kb_dir / "documents.json"
    if not documents_path.exists():
        return []
    
    with open(documents_path, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    # Extract unique restaurant names
    restaurant_names = set()
    for doc in documents:
        if doc["type"] == "restaurant":
            restaurant_names.add(doc["metadata"]["name"])
    
    return sorted(list(restaurant_names))

def get_dietary_options() -> List[str]:
    """
    Get a list of dietary options supported by the system.
    
    Returns:
        List of dietary options
    """
    return [
        "vegetarian",
        "vegan",
        "gluten-free",
        "dairy-free",
        "nut-free",
        "spicy"
    ]

def format_price_range(min_price: float, max_price: float) -> str:
    """
    Format a price range as a string.
    
    Args:
        min_price: Minimum price
        max_price: Maximum price
        
    Returns:
        Formatted price range string
    """
    return f"${min_price:.2f} - ${max_price:.2f}"

def extract_price_value(price_str: str) -> Optional[float]:
    """
    Extract a numeric price value from a price string.
    
    Args:
        price_str: Price string (e.g., "$12.99")
        
    Returns:
        Numeric price value or None if extraction failed
    """
    import re
    
    if not price_str:
        return None
    
    # Try to extract a price value
    match = re.search(r'\$(\d+(?:\.\d{2})?)', price_str)
    if match:
        return float(match.group(1))
    
    return None

def categorize_restaurants_by_cuisine(documents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Categorize restaurants by cuisine type based on menu items.
    
    Args:
        documents: List of documents from the knowledge base
        
    Returns:
        Dictionary mapping cuisine types to lists of restaurant names
    """
    # Define cuisine keywords
    cuisine_keywords = {
        "Italian": ["pasta", "pizza", "risotto", "italian", "tiramisu", "lasagna", "spaghetti"],
        "Mexican": ["taco", "burrito", "quesadilla", "mexican", "enchilada", "salsa", "guacamole"],
        "Chinese": ["wonton", "dumpling", "chinese", "noodle", "stir-fry", "dim sum", "kung pao"],
        "Japanese": ["sushi", "sashimi", "ramen", "japanese", "tempura", "teriyaki", "miso"],
        "Indian": ["curry", "tandoori", "naan", "indian", "masala", "biryani", "samosa"],
        "Thai": ["pad thai", "thai", "curry", "tom yum", "satay"],
        "American": ["burger", "american", "steak", "bbq", "fried chicken", "hot dog"]
    }
    
    # Initialize result dictionary
    cuisine_restaurants = {cuisine: [] for cuisine in cuisine_keywords}
    
    # Create a mapping of restaurants to their menu items
    restaurant_menu_items = {}
    
    # Extract menu items for each restaurant
    for doc in documents:
        if doc["type"] == "menu_item":
            restaurant_name = doc["metadata"]["restaurant"]
            item_name = doc["metadata"]["name"].lower()
            item_description = doc["metadata"].get("description", "").lower()
            
            if restaurant_name not in restaurant_menu_items:
                restaurant_menu_items[restaurant_name] = []
            
            restaurant_menu_items[restaurant_name].append({
                "name": item_name,
                "description": item_description
            })
    
    # Categorize restaurants by cuisine
    for restaurant, menu_items in restaurant_menu_items.items():
        cuisine_scores = {cuisine: 0 for cuisine in cuisine_keywords}
        
        # Calculate score for each cuisine based on menu items
        for item in menu_items:
            for cuisine, keywords in cuisine_keywords.items():
                for keyword in keywords:
                    if keyword in item["name"] or keyword in item["description"]:
                        cuisine_scores[cuisine] += 1
        
        # Find the cuisine with the highest score
        if cuisine_scores:
            top_cuisine = max(cuisine_scores.items(), key=lambda x: x[1])
            if top_cuisine[1] > 0:  # Only categorize if there's a match
                cuisine_restaurants[top_cuisine[0]].append(restaurant)
    
    return cuisine_restaurants 