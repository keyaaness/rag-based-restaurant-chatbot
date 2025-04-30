"""
Restaurant Configuration Module

This module contains configurations for scraping specific restaurant websites.
Each configuration includes the restaurant name, URL, and CSS selectors for
extracting the required data.
"""

# List of restaurant configurations for scraping
RESTAURANT_CONFIGS = [
    {
        "name": "The Italian Restaurant",
        "url": "https://www.theitalianrestaurant.com",  # Example URL
        "selectors": {
            "menu_section": "div.menu-section",
            "menu_section_name": "h2.section-title",
            "menu_item": "div.menu-item",
            "item_name": "h3.item-name",
            "item_price": "span.price",
            "item_description": "p.description",
            "dietary_info": "span.dietary-info",
            "location": "div.location address",
            "hours_section": "div.hours",
            "contact_section": "div.contact-info",
            "special_features": "div.features span"
        }
    },
    {
        "name": "Spice Garden",
        "url": "https://www.spicegarden.com",  # Example URL
        "selectors": {
            "menu_section": "section.menu-category",
            "menu_section_name": "h2.category-name",
            "menu_item": "div.dish",
            "item_name": "h4.dish-name",
            "item_price": "span.dish-price",
            "item_description": "p.dish-description",
            "dietary_info": "div.dish-tags span",
            "location": "div.restaurant-address",
            "hours_section": "div.opening-hours",
            "contact_section": "div.contact",
            "special_features": "ul.features li"
        }
    },
    {
        "name": "Burger Joint",
        "url": "https://www.burgerjoint.com",  # Example URL
        "selectors": {
            "menu_section": "div.menu-category",
            "menu_section_name": "h3.category-title",
            "menu_item": "div.burger-item",
            "item_name": "h4.burger-name",
            "item_price": "div.burger-price",
            "item_description": "p.burger-description",
            "dietary_info": "div.burger-tags span",
            "location": "div.store-location",
            "hours_section": "div.store-hours",
            "contact_section": "div.contact-details",
            "special_features": "div.specials li"
        }
    },
    {
        "name": "Sushi Express",
        "url": "https://www.sushiexpress.com",  # Example URL
        "selectors": {
            "menu_section": "div.sushi-category",
            "menu_section_name": "h2.category-name",
            "menu_item": "div.sushi-item",
            "item_name": "h3.sushi-name",
            "item_price": "span.sushi-price",
            "item_description": "p.sushi-description",
            "dietary_info": "span.sushi-tags",
            "location": "div.restaurant-location",
            "hours_section": "div.business-hours",
            "contact_section": "div.contact-info",
            "special_features": "ul.restaurant-features li"
        }
    },
    {
        "name": "Taco Haven",
        "url": "https://www.tacohaven.com",  # Example URL
        "selectors": {
            "menu_section": "section.menu-section",
            "menu_section_name": "h3.section-title",
            "menu_item": "div.taco-item",
            "item_name": "h4.taco-name",
            "item_price": "span.taco-price",
            "item_description": "p.taco-description",
            "dietary_info": "div.taco-info span",
            "location": "div.location-info",
            "hours_section": "div.hours-section",
            "contact_section": "div.contact-section",
            "special_features": "ul.features li"
        }
    },
    {
        "name": "Golden Dragon",
        "url": "https://www.goldendragon.com",  # Example URL
        "selectors": {
            "menu_section": "div.menu-category",
            "menu_section_name": "h2.category-title",
            "menu_item": "div.dish-item",
            "item_name": "h3.dish-title",
            "item_price": "span.dish-price",
            "item_description": "p.dish-description",
            "dietary_info": "div.dish-attributes span",
            "location": "div.restaurant-address",
            "hours_section": "div.opening-times",
            "contact_section": "div.contact-details",
            "special_features": "ul.special-features li"
        }
    },
    {
        "name": "Pizzeria Napoli",
        "url": "https://www.pizzerianapoli.com",  # Example URL
        "selectors": {
            "menu_section": "section.pizza-category",
            "menu_section_name": "h2.category-name",
            "menu_item": "div.pizza-item",
            "item_name": "h3.pizza-name",
            "item_price": "div.pizza-price",
            "item_description": "p.pizza-description",
            "dietary_info": "div.pizza-options span",
            "location": "div.pizzeria-location",
            "hours_section": "div.opening-hours",
            "contact_section": "div.pizzeria-contact",
            "special_features": "ul.pizzeria-features li"
        }
    },
    {
        "name": "Mediterranean Delight",
        "url": "https://www.mediterraneandelight.com",  # Example URL
        "selectors": {
            "menu_section": "div.menu-section",
            "menu_section_name": "h3.section-header",
            "menu_item": "div.food-item",
            "item_name": "h4.food-name",
            "item_price": "span.food-price",
            "item_description": "p.food-description",
            "dietary_info": "div.food-dietary span",
            "location": "div.restaurant-address",
            "hours_section": "div.business-hours",
            "contact_section": "div.contact-information",
            "special_features": "ul.restaurant-highlights li"
        }
    }
]

# Function to get restaurant configurations
def get_restaurant_configs():
    """
    Get the list of restaurant configurations for scraping.
    
    Returns:
        List of restaurant configuration dictionaries
    """
    return RESTAURANT_CONFIGS

# Function to get a specific restaurant configuration by name
def get_restaurant_config_by_name(name):
    """
    Get a specific restaurant configuration by name.
    
    Args:
        name: Name of the restaurant
        
    Returns:
        Restaurant configuration dictionary or None if not found
    """
    for config in RESTAURANT_CONFIGS:
        if config["name"].lower() == name.lower():
            return config
    return None 