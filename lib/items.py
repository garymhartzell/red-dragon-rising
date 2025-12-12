# Equipment and item handling functions for Red Dragon Rising

import json

def load_items(category):
    """Loads item data from the corresponding JSON file."""
    file_map = {
        "weapons": "assets/item_weapons.json",
        "armor": "assets/item_armor.json"
    }

    file_path = file_map.get(category, "")

    if not file_path:
        return {}  # Empty dictionary if category isn't found

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

            if isinstance(data, list):  # Convert list to dict if needed
                return {str(item["item_id"]): item for item in data}

            return data  # Ensure it's returning a dictionary
        
    except FileNotFoundError:
        return {}

def get_item_stat(item_id, category, stat):
    """Retrieves a specific stat (name, attack, cost, etc.) for an item."""
    items = load_items(category)
    return items[category].get(str(item_id), {}).get(stat, "Unknown Stat")

def get_item_info(item_id, category):
    """Retrieves all stats for an item."""
    items = load_items(category)
    return items[category].get(str(item_id), {})

def get_available_items(category, player_level):
    """Fetches items from the specified category that the player is eligible to purchase."""
    items = load_items(category)  # Load item data

    available_items = {item_id: item for item_id, item in items[category].items() if item["level_unlocked"] <= player_level}
    
    return available_items
