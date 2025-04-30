"""
Restaurant Scraper Module

This module provides functionality to scrape data from restaurant websites including
menus, locations, operating hours, and other details.
"""

import os
import json
import re
import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

class RestaurantScraper:
    """Class for scraping restaurant data from websites."""
    
    def __init__(self, output_dir: str = "data/raw"):
        """
        Initialize the restaurant scraper.
        
        Args:
            output_dir: Directory where scraped data will be saved
        """
        self.output_dir = output_dir
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Get and parse the content of a web page.
        
        Args:
            url: The URL of the web page to scrape
            
        Returns:
            BeautifulSoup object containing the parsed HTML content, or None if the request failed
        """
        try:
            # Add a random delay to avoid aggressive scraping
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML content
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def scrape_restaurant(self, restaurant_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scrape data for a single restaurant based on configuration.
        
        Args:
            restaurant_config: Dictionary containing scraping configuration for the restaurant
                {
                    "name": "Restaurant Name",
                    "url": "https://restaurant-website.com",
                    "selectors": {
                        "menu_items": "...",
                        "location": "...",
                        ...
                    }
                }
                
        Returns:
            Dictionary containing scraped restaurant data
        """
        name = restaurant_config["name"]
        url = restaurant_config["url"]
        selectors = restaurant_config.get("selectors", {})
        
        print(f"Scraping data for {name} from {url}")
        
        # Initialize restaurant data
        restaurant_data = {
            "name": name,
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "location": {},
            "menu_items": [],
            "operating_hours": {},
            "contact_info": {},
            "special_features": []
        }
        
        # Get page content
        soup = self._get_page_content(url)
        if not soup:
            print(f"Failed to fetch content for {name}")
            return restaurant_data
        
        # Extract restaurant details using provided selectors and custom logic
        # This is a generic implementation - specific implementations would be customized
        # for each restaurant website structure
        
        # Example: Extract location information
        if "location" in selectors:
            location_elem = soup.select_one(selectors["location"])
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                # Simple parsing logic - would need to be customized
                restaurant_data["location"] = {
                    "address": location_text,
                    "city": self._extract_city(location_text),
                    "state": self._extract_state(location_text)
                }
        
        # Example: Extract menu items
        if "menu_section" in selectors:
            menu_sections = soup.select(selectors["menu_section"])
            for section in menu_sections:
                section_name = section.select_one(selectors.get("menu_section_name", "h2, h3")).get_text(strip=True)
                menu_items = section.select(selectors.get("menu_item", "div.menu-item"))
                
                for item in menu_items:
                    # Extract menu item details
                    item_name = item.select_one(selectors.get("item_name", "h4, .item-name")).get_text(strip=True) if item.select_one(selectors.get("item_name", "h4, .item-name")) else "Unknown Item"
                    
                    # Extract price - handle different formats
                    price_elem = item.select_one(selectors.get("item_price", ".price"))
                    price = price_elem.get_text(strip=True) if price_elem else "Price not available"
                    
                    # Clean price format
                    price = self._clean_price(price)
                    
                    # Extract description
                    desc_elem = item.select_one(selectors.get("item_description", ".description"))
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Extract dietary info and special notes
                    dietary_info = self._extract_dietary_info(item, description, selectors.get("dietary_info", ".dietary"))
                    
                    menu_item = {
                        "name": item_name,
                        "price": price,
                        "description": description,
                        "section": section_name,
                        "dietary_info": dietary_info
                    }
                    
                    restaurant_data["menu_items"].append(menu_item)
        
        # Example: Extract operating hours
        if "hours_section" in selectors:
            hours_elem = soup.select_one(selectors["hours_section"])
            if hours_elem:
                days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                for day in days_of_week:
                    day_elem = hours_elem.find(lambda tag: tag.name and day.lower() in tag.get_text().lower())
                    if day_elem:
                        hours_text = day_elem.get_text(strip=True)
                        hours_match = re.search(r'\d{1,2}:\d{2}\s*(?:AM|PM)\s*-\s*\d{1,2}:\d{2}\s*(?:AM|PM)', hours_text, re.IGNORECASE)
                        if hours_match:
                            restaurant_data["operating_hours"][day] = hours_match.group(0)
                        else:
                            restaurant_data["operating_hours"][day] = "Closed" if "closed" in hours_text.lower() else hours_text
        
        # Example: Extract contact information
        if "contact_section" in selectors:
            contact_elem = soup.select_one(selectors["contact_section"])
            if contact_elem:
                # Phone
                phone_elem = contact_elem.find(lambda tag: tag.name and re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', tag.get_text()))
                if phone_elem:
                    phone_match = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', phone_elem.get_text())
                    if phone_match:
                        restaurant_data["contact_info"]["phone"] = phone_match.group(0)
                
                # Email
                email_elem = contact_elem.find(lambda tag: tag.name and re.search(r'[\w\.-]+@[\w\.-]+', tag.get_text()))
                if email_elem:
                    email_match = re.search(r'[\w\.-]+@[\w\.-]+', email_elem.get_text())
                    if email_match:
                        restaurant_data["contact_info"]["email"] = email_match.group(0)
        
        # Example: Extract special features
        if "special_features" in selectors:
            feature_elems = soup.select(selectors["special_features"])
            for elem in feature_elems:
                feature_text = elem.get_text(strip=True)
                restaurant_data["special_features"].append(feature_text)
        
        return restaurant_data
    
    def _extract_city(self, address_text: str) -> str:
        """Extract city from address text."""
        # This is a simplified implementation
        # In a real implementation, you would use a more robust approach
        city_match = re.search(r'([A-Z][a-z]+),\s*[A-Z]{2}', address_text)
        return city_match.group(1) if city_match else ""
    
    def _extract_state(self, address_text: str) -> str:
        """Extract state from address text."""
        # This is a simplified implementation
        state_match = re.search(r',\s*([A-Z]{2})', address_text)
        return state_match.group(1) if state_match else ""
    
    def _clean_price(self, price_text: str) -> str:
        """Clean and normalize price text."""
        # Remove any non-price characters
        price_match = re.search(r'(\$\d+(?:\.\d{2})?)', price_text)
        return price_match.group(0) if price_match else price_text
    
    def _extract_dietary_info(self, item_elem, description: str, selector: str) -> List[str]:
        """Extract dietary information from menu item."""
        dietary_info = []
        
        # Check for explicit dietary labels
        if selector:
            dietary_elems = item_elem.select(selector)
            for elem in dietary_elems:
                dietary_info.append(elem.get_text(strip=True))
        
        # Infer from description text
        keywords = {
            "vegetarian": ["vegetarian", "veg"],
            "vegan": ["vegan"],
            "gluten-free": ["gluten-free", "gluten free", "gf"],
            "spicy": ["spicy", "hot", "🌶️", "🔥"],
            "contains nuts": ["nuts", "peanuts", "almonds", "walnuts"],
            "dairy-free": ["dairy-free", "dairy free", "df"]
        }
        
        description_lower = description.lower()
        for category, terms in keywords.items():
            for term in terms:
                if term in description_lower and category not in dietary_info:
                    dietary_info.append(category)
                    break
        
        return dietary_info
    
    def save_data(self, restaurant_data: Dict[str, Any], filename: str = None) -> None:
        """
        Save the scraped restaurant data to a JSON file.
        
        Args:
            restaurant_data: Dictionary containing scraped restaurant data
            filename: Optional custom filename, otherwise generated from restaurant name
        """
        if filename is None:
            # Create filename from restaurant name
            restaurant_name = restaurant_data["name"]
            filename = f"{restaurant_name.lower().replace(' ', '_')}.json"
        
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(restaurant_data, f, indent=2, ensure_ascii=False)
        
        print(f"Saved data for {restaurant_data['name']} to {file_path}")
    
    def scrape_multiple_restaurants(self, restaurant_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scrape data for multiple restaurants.
        
        Args:
            restaurant_configs: List of restaurant configuration dictionaries
            
        Returns:
            List of dictionaries containing scraped restaurant data
        """
        all_restaurant_data = []
        
        for config in tqdm(restaurant_configs, desc="Scraping restaurants"):
            restaurant_data = self.scrape_restaurant(config)
            self.save_data(restaurant_data)
            all_restaurant_data.append(restaurant_data)
        
        return all_restaurant_data 