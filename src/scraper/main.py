"""
Main Scraper Script

This script is the entry point for the restaurant data scraping process.
It uses the RestaurantScraper class to collect data from restaurant websites
based on the configurations specified in restaurant_configs.py.
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.restaurant_scraper import RestaurantScraper
from scraper.restaurant_configs import get_restaurant_configs, get_restaurant_config_by_name

def main():
    """
    Main function to run the scraper.
    """
    parser = argparse.ArgumentParser(description="Scrape restaurant data from websites.")
    parser.add_argument(
        "--restaurant", 
        type=str, 
        help="Name of a specific restaurant to scrape. If not provided, all restaurants will be scraped."
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="data/raw", 
        help="Directory to save scraped data. Default is 'data/raw'."
    )
    parser.add_argument(
        "--timeout", 
        type=float, 
        default=10.0, 
        help="Timeout for HTTP requests in seconds. Default is 10.0."
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode with more verbose output."
    )
    parser.add_argument(
        "--mock", 
        action="store_true", 
        help="Use mock data instead of actual scraping (for testing)."
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize the scraper
    scraper = RestaurantScraper(output_dir=args.output)
    
    if args.mock:
        # Use mock data for testing (without actual web scraping)
        print("Using mock data (no actual web scraping)")
        generate_mock_data(output_dir)
        return
    
    # Get restaurant configurations
    if args.restaurant:
        # Scrape a specific restaurant
        restaurant_config = get_restaurant_config_by_name(args.restaurant)
        if restaurant_config:
            print(f"Scraping data for restaurant: {restaurant_config['name']}")
            restaurant_data = scraper.scrape_restaurant(restaurant_config)
            scraper.save_data(restaurant_data)
        else:
            print(f"Restaurant '{args.restaurant}' not found in configurations.")
            return
    else:
        # Scrape all restaurants
        restaurant_configs = get_restaurant_configs()
        print(f"Scraping data for {len(restaurant_configs)} restaurants...")
        scraper.scrape_multiple_restaurants(restaurant_configs)
    
    print("Scraping completed successfully.")

def generate_mock_data(output_dir: Path) -> None:
    """
    Generate mock data for testing without actual web scraping.
    
    Args:
        output_dir: Directory to save mock data
    """
    restaurant_configs = get_restaurant_configs()
    
    for config in restaurant_configs:
        name = config["name"]
        print(f"Generating mock data for {name}")
        
        # Create mock restaurant data
        mock_data = {
            "name": name,
            "url": config["url"],
            "scraped_at": "2023-04-25T12:00:00",
            "location": {
                "address": "123 Main St, Foodville, CA 94123",
                "city": "Foodville",
                "state": "CA"
            },
            "menu_items": []
        }
        
        # Generate mock menu items based on restaurant type
        if "Italian" in name:
            sections = ["Appetizers", "Pasta", "Pizza", "Desserts"]
            items_per_section = 5
            for section in sections:
                for i in range(1, items_per_section + 1):
                    item = {
                        "name": f"{section} Item {i}",
                        "price": f"${(i * 2) + 5:.2f}",
                        "description": f"Delicious {section.lower()} made with fresh ingredients.",
                        "section": section,
                        "dietary_info": ["vegetarian"] if i % 2 == 0 else []
                    }
                    mock_data["menu_items"].append(item)
        elif "Burger" in name:
            sections = ["Burgers", "Sides", "Shakes", "Specials"]
            items_per_section = 4
            for section in sections:
                for i in range(1, items_per_section + 1):
                    item = {
                        "name": f"{section} Item {i}",
                        "price": f"${(i * 2) + 6:.2f}",
                        "description": f"Classic {section.lower()} with our special sauce.",
                        "section": section,
                        "dietary_info": ["gluten-free"] if i % 3 == 0 else []
                    }
                    mock_data["menu_items"].append(item)
        else:
            # Generic menu items
            sections = ["Starters", "Main Courses", "Specials", "Drinks"]
            items_per_section = 4
            for section in sections:
                for i in range(1, items_per_section + 1):
                    item = {
                        "name": f"{section} Item {i}",
                        "price": f"${(i * 3) + 4:.2f}",
                        "description": f"House specialty {section.lower()}.",
                        "section": section,
                        "dietary_info": ["vegan"] if i % 4 == 0 else []
                    }
                    mock_data["menu_items"].append(item)
        
        # Add operating hours
        mock_data["operating_hours"] = {
            "Monday": "11:00 AM - 9:00 PM",
            "Tuesday": "11:00 AM - 9:00 PM",
            "Wednesday": "11:00 AM - 9:00 PM",
            "Thursday": "11:00 AM - 10:00 PM",
            "Friday": "11:00 AM - 11:00 PM",
            "Saturday": "10:00 AM - 11:00 PM",
            "Sunday": "10:00 AM - 8:00 PM"
        }
        
        # Add contact info
        mock_data["contact_info"] = {
            "phone": "(555) 123-4567",
            "email": f"info@{name.lower().replace(' ', '')}.com"
        }
        
        # Add special features
        mock_data["special_features"] = [
            "Outdoor Seating",
            "Takeout Available",
            "Delivery",
            "Vegetarian Options"
        ]
        
        # Save mock data
        file_path = output_dir / f"{name.lower().replace(' ', '_')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(mock_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()