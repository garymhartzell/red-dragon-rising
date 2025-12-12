# Red Dragon Rising - View Stats

from flask import render_template
from lib.character import get_char_stat
from lib.items import get_item_stat

def view_stats_page():
    """
    Renders the view stats page, displaying character and inventory statistics.
    """
    character_stats = {
        "name": get_char_stat('name'),
        "xp": get_char_stat('xp'),
        "level": get_char_stat('level'),
        "rank": get_char_stat('rank'),
        "hp": get_char_stat('hp'),
        "max_hp": get_char_stat('max_hp'),
        "stamina": get_char_stat('stamina'),
        "offense": get_char_stat('offense'),
        "defense": get_char_stat('defense'),
        "gender": get_char_stat('gender'),
        "charm": get_char_stat('charm'),
    }

    inventory_stats = {
        "gold_hand": get_char_stat('gold_hand'),
        "gold_bank": get_char_stat('gold_bank'),
        "gems_hand": get_char_stat('gems_hand'),
        "gems_bank": get_char_stat('gems_bank'),
        "weapon": get_item_stat(get_char_stat('weapon_id'), "weapons", "item_name"),
        "armor": get_item_stat(get_char_stat('armor_id'), "armor", "item_name") if get_char_stat('armor_id') else "None",
        "horse": get_item_stat(get_char_stat('horse_id'), "horses", "item_name") if get_char_stat('horse_id') else "None",
        "healing_potions": get_char_stat('healing_potions'),
    }
    
    return render_template("view_stats.html", character=character_stats, inventory=inventory_stats)
    
