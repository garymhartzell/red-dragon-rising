# Functions for handling character stats, settings, etc.

import json
import os


CHAR_FILE = "assets/character.json"

def ensure_character_file():
    """Creates an empty character file if it doesn't exist."""
    if not os.path.exists(CHAR_FILE):
        default_character = {}
        with open(CHAR_FILE, "w") as file:
            json.dump(default_character, file, indent=4)
            
def load_character():
    """Loads character data from JSON."""
    ensure_character_file()
    with open(CHAR_FILE, "r") as file:
        return json.load(file)

def save_character(character):
    """Saves character data back to JSON."""
    with open(CHAR_FILE, "w") as file:
        json.dump(character, file, indent=4)

def get_char_stat(stat):
    """Retrieves a specific stat."""
    character = load_character()
    return character.get(stat, "Unknown Stat")

def set_char_stat(stat, value):
    """Sets a character stat to a new value."""
    character = load_character()
    character[stat] = value
    save_character(character)

def increment_char_stat(stat, value):
    """Adds or subtracts from a character stat."""
    character = load_character()
    character[stat] = character.get(stat, 0) + value
    save_character(character)
