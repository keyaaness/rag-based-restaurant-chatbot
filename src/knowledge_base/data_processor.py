"""
Data Processor Module

This module processes the scraped restaurant data and prepares it for the knowledge base.
It includes cleaning, normalization, and structuring the data for efficient retrieval.
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from tqdm import tqdm

class DataProcessor:
    """Class for processing scraped restaurant data."""
    
    def __init__(self, input_dir: str = "data/raw", output_dir: str = "data/processed"):
        """
        Initialize the data processor.
        
        Args:
            input_dir: Directory containing raw scraped data
            output_dir: Directory where processed data will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def load_restaurant_data(self, filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Load restaurant data from JSON files.
        
        Args:
            filename: Optional specific file to load. If None, all files in input_dir are loaded.
            
        Returns:
            List of dictionaries containing restaurant data
        """
        restaurant_data = []
        
        if filename:
            # Load a specific file
            file_path = self.input_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    restaurant_data.append(data)
            else:
                print(f"File not found: {file_path}")
        else:
            # Load all JSON files in the input directory
            json_files = list(self.input_dir.glob('*.json'))
            
            if not json_files:
                print(f"No JSON files found in {self.input_dir}")
                return restaurant_data
            
            for file_path in tqdm(json_files, desc="Loading restaurant data"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    restaurant_data.append(data)
        
        return restaurant_data
    
    def clean_restaurant_data(self, restaurants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean and normalize restaurant data.
        
        Args:
            restaurants: List of restaurant data dictionaries
            
        Returns:
            List of cleaned restaurant data dictionaries
        """
        cleaned_restaurants = []
        
        for restaurant in tqdm(restaurants, desc="Cleaning restaurant data"):
            cleaned_restaurant = restaurant.copy()
            
            # Clean restaurant name (remove extra spaces, special characters, etc.)
            if "name" in cleaned_restaurant:
                cleaned_restaurant["name"] = self._clean_text(cleaned_restaurant["name"])
            
            # Clean menu items
            if "menu_items" in cleaned_restaurant:
                cleaned_menu_items = []
                for item in cleaned_restaurant["menu_items"]:
                    cleaned_item = item.copy()
                    
                    # Clean item name
                    if "name" in cleaned_item:
                        cleaned_item["name"] = self._clean_text(cleaned_item["name"])
                    
                    # Clean item description
                    if "description" in cleaned_item:
                        cleaned_item["description"] = self._clean_text(cleaned_item["description"])
                    
                    # Clean and normalize price
                    if "price" in cleaned_item:
                        cleaned_item["price"] = self._normalize_price(cleaned_item["price"])
                    
                    # Ensure dietary info is a list of strings
                    if "dietary_info" in cleaned_item:
                        if not isinstance(cleaned_item["dietary_info"], list):
                            cleaned_item["dietary_info"] = [str(cleaned_item["dietary_info"])]
                        else:
                            cleaned_item["dietary_info"] = [self._clean_text(info) for info in cleaned_item["dietary_info"]]
                    
                    cleaned_menu_items.append(cleaned_item)
                
                cleaned_restaurant["menu_items"] = cleaned_menu_items
            
            # Clean location data
            if "location" in cleaned_restaurant and isinstance(cleaned_restaurant["location"], dict):
                for key in cleaned_restaurant["location"]:
                    if isinstance(cleaned_restaurant["location"][key], str):
                        cleaned_restaurant["location"][key] = self._clean_text(cleaned_restaurant["location"][key])
            
            # Clean operating hours
            if "operating_hours" in cleaned_restaurant and isinstance(cleaned_restaurant["operating_hours"], dict):
                for day, hours in cleaned_restaurant["operating_hours"].items():
                    cleaned_restaurant["operating_hours"][day] = self._clean_text(hours)
            
            # Clean contact info
            if "contact_info" in cleaned_restaurant and isinstance(cleaned_restaurant["contact_info"], dict):
                for key in cleaned_restaurant["contact_info"]:
                    if isinstance(cleaned_restaurant["contact_info"][key], str):
                        cleaned_restaurant["contact_info"][key] = self._clean_text(cleaned_restaurant["contact_info"][key])
            
            # Clean special features
            if "special_features" in cleaned_restaurant:
                if isinstance(cleaned_restaurant["special_features"], list):
                    cleaned_restaurant["special_features"] = [self._clean_text(feature) for feature in cleaned_restaurant["special_features"]]
                else:
                    cleaned_restaurant["special_features"] = []
            
            cleaned_restaurants.append(cleaned_restaurant)
        
        return cleaned_restaurants
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return str(text)
        
        # Remove extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        # Replace HTML entities
        cleaned_text = cleaned_text.replace('&amp;', '&')
        cleaned_text = cleaned_text.replace('&lt;', '<')
        cleaned_text = cleaned_text.replace('&gt;', '>')
        cleaned_text = cleaned_text.replace('&quot;', '"')
        cleaned_text = cleaned_text.replace('&apos;', "'")
        
        return cleaned_text
    
    def _normalize_price(self, price: str) -> str:
        """
        Normalize price format.
        
        Args:
            price: Price string to normalize
            
        Returns:
            Normalized price string
        """
        if not isinstance(price, str):
            return str(price)
        
        # Extract price value from string
        price_match = re.search(r'(\$\d+(?:\.\d{2})?)', price)
        if price_match:
            return price_match.group(1)
        
        # If no standard price format is found, return as is
        return price
    
    def create_menu_items_dataframe(self, restaurants: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a DataFrame of all menu items across restaurants.
        
        Args:
            restaurants: List of restaurant data dictionaries
            
        Returns:
            DataFrame containing menu items
        """
        all_items = []
        
        for restaurant in restaurants:
            restaurant_name = restaurant.get("name", "Unknown Restaurant")
            
            for item in restaurant.get("menu_items", []):
                item_data = {
                    "restaurant": restaurant_name,
                    "name": item.get("name", ""),
                    "price": item.get("price", ""),
                    "description": item.get("description", ""),
                    "section": item.get("section", ""),
                    "dietary_info": ", ".join(item.get("dietary_info", []))
                }
                all_items.append(item_data)
        
        return pd.DataFrame(all_items)
    
    def create_restaurants_dataframe(self, restaurants: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create a DataFrame of restaurant information.
        
        Args:
            restaurants: List of restaurant data dictionaries
            
        Returns:
            DataFrame containing restaurant information
        """
        restaurant_info = []
        
        for restaurant in restaurants:
            # Extract location info
            location = restaurant.get("location", {})
            address = location.get("address", "")
            city = location.get("city", "")
            state = location.get("state", "")
            
            # Extract contact info
            contact_info = restaurant.get("contact_info", {})
            phone = contact_info.get("phone", "")
            email = contact_info.get("email", "")
            
            # Format operating hours
            operating_hours = restaurant.get("operating_hours", {})
            hours_str = ", ".join([f"{day}: {hours}" for day, hours in operating_hours.items()])
            
            # Format special features
            special_features = ", ".join(restaurant.get("special_features", []))
            
            restaurant_data = {
                "name": restaurant.get("name", ""),
                "url": restaurant.get("url", ""),
                "address": address,
                "city": city,
                "state": state,
                "phone": phone,
                "email": email,
                "hours": hours_str,
                "special_features": special_features
            }
            restaurant_info.append(restaurant_data)
        
        return pd.DataFrame(restaurant_info)
    
    def process_data(self) -> None:
        """
        Process the restaurant data and save it to CSV files.
        """
        # Load raw restaurant data
        restaurants = self.load_restaurant_data()
        
        if not restaurants:
            print("No restaurant data to process.")
            return
        
        # Clean and normalize the data
        cleaned_restaurants = self.clean_restaurant_data(restaurants)
        
        # Create DataFrames
        menu_items_df = self.create_menu_items_dataframe(cleaned_restaurants)
        restaurants_df = self.create_restaurants_dataframe(cleaned_restaurants)
        
        # Save processed data
        menu_items_df.to_csv(self.output_dir / "menu_items.csv", index=False)
        restaurants_df.to_csv(self.output_dir / "restaurants.csv", index=False)
        
        # Save cleaned JSON data for each restaurant
        for restaurant in cleaned_restaurants:
            name = restaurant.get("name", "unknown")
            filename = f"{name.lower().replace(' ', '_')}.json"
            with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(restaurant, f, indent=2, ensure_ascii=False)
        
        print(f"Processed data saved to {self.output_dir}")
        print(f"Total restaurants: {len(cleaned_restaurants)}")
        print(f"Total menu items: {len(menu_items_df)}") 