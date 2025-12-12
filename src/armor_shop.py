# Red Dragon Rising Armor Shop

from pywebio.output import put_buttons, put_text, put_markdown, put_html, clear
from pywebio.input import radio
from lib.goto import goto
from lib.character import set_char_stat, get_char_stat
from lib.items import get_item_stat, get_available_items
import random

def armor_shop():
    clear()
    set_char_stat("location", "armor_shop")
    put_html("<script>document.title = 'Red Dragon Rising - Able's Armor'</script>")
    put_markdown(f"""
        # Able's Armor

        The shop’s entrance bears a well-worn plaque: "Able’s Armor – Crafted for the Bold." Inside, polished shields glint under lantern light, and carefully arranged suits of armor stand like silent sentinels. A soft melody lingers in the air—a bard’s tune, woven from memories of a father’s songs and a daughter’s craftsmanship.
        
        Behind the counter stands Jenifer Able, the daughter of the legendary bard Seth Able. Though she does not wield a lute like her father, she carries his legacy in another way—ensuring every warrior who enters Able’s Armor leaves with protection befitting their stature.
        
        You have {get_char_stat("gold_hand")} gold on hand.
        
        Jenifer looks at you expectantly.
    """)
    put_buttons(["Buy armor", "Sell your armor", "View Stats", "Leave"],
        onclick=[buy_armor, sell_armor, lambda: goto("view_stats"), lambda: goto("town_square")])
        
def buy_armor():
    current_armor_id = int(get_char_stat("armor_id"))
    if 201 <= current_armor_id <= 299:
        armor_name = get_item_stat(current_armor_id, "armor", "item_name")
        put_text(f'Jenifer tells you, "You already have armor. Would you like to sell your {armor_name}?"')
        put_buttons(["Yes", "No"], onclick=[sell_armor, armor_shop])
        return
    else:
        clear()
        put_html("<script>document.title = 'Red Dragon Rising - Able&apos;s Armor'</script>")
        put_markdown("""
        ## Able's Armor
        
        Jenifer regards you with a measured expression, inspecting your stance as she would a set of newly forged plate mail.  With practiced hands, she unfurls a parchment detailing the available gear, each piece meticulously crafted to withstand the trials of this World.
        
        What armor do you choose?
        """)
        
        player_level = get_char_stat("level")  
        armor_items = get_available_items("armor", player_level)
        put_buttons(
            [f"{armor_piece['item_name']} ({armor_piece['cost']} gold)" for armor_piece in armor_items.values()] + ["Cancel"], 
            onclick=[lambda w=item_id: confirm_armor_purchase(w) for item_id in armor_items.keys()] + [armor_shop] 
        )
        
def confirm_armor_purchase(item_id):
    armor_name = get_item_stat(item_id, "armor", "item_name")
    armor_price = get_item_stat(item_id, "armor", "cost")

    put_text(f'Jenifer smiles. "Good choice. {armor_name} will cost you {armor_price} gold. Do you want it?"')
    put_buttons(["Yes", "No"], onclick=[lambda: finalize_armor_purchase(item_id), armor_shop])

def finalize_armor_purchase(item_id):
    gold_hand = get_char_stat("gold_hand")
    armor_price = get_item_stat(item_id, "armor", "cost")
    armor_boost = get_item_stat(item_id, "armor", "boost")  
    char_defense = get_char_stat("defense")

    if gold_hand < weapon_price:
        put_text("You don't have enough gold to buy this weapon.")
        return

    set_char_stat("gold_hand", gold_hand - weapon_price)
    set_char_stat("weapon_id", item_id)
    set_char_stat("offense", char_offense+weapon_boost)
    
    put_text(f"You have purchased a {get_item_stat(item_id, 'weapons', 'item_name')}!")
    put_buttons(["Continue"], onclick=[lambda: goto('town_square')])

def sell_weapon():
    current_weapon_id = int(get_char_stat("weapon_id"))

    # Ensure player has a weapon to sell
    if not (101 <= current_weapon_id <= 199):
        put_text("You don't have a weapon to sell.")
        put_buttons(["Continue"], onclick=[weapon_shop])
        return

    weapon_name = get_item_stat(current_weapon_id, "weapons", "item_name")
    sell_min = get_item_stat(current_weapon_id, "weapons", "sell_min")
    sell_max = get_item_stat(current_weapon_id, "weapons", "sell_max")

    # Randomized selling price within range
    sell_price = random.randint(sell_min, sell_max)

    clear()
    put_html("<script>document.title = 'Red Dragon Rising - Mid World Weaponry'</script>")
    put_markdown(f"""
    ## Mid World Weaponry
    
    You tell the shopkeeper that you wish to sell your {weapon_name}. He takes it from you, looking it over thoughtfully.
    
    "I can offer you {sell_price} gold for this {weapon_name}. Do we have a deal?"
    """)
    put_buttons(["Yes", "No"], onclick=[lambda: finalize_weapon_sale(current_weapon_id, sell_price), weapon_shop])

def finalize_weapon_sale(item_id, sell_price):
    gold_hand = get_char_stat("gold_hand")
    char_offense = get_char_stat("offense")
    weapon_boost = get_item_stat(item_id, "weapons", "boost")

    # Calculate new offense while ensuring it doesn’t drop below 0
    new_offense = max(0, char_offense - weapon_boost)

    # Update player stats
    set_char_stat("gold_hand", gold_hand + sell_price)
    set_char_stat("weapon_id", 0) 
    set_char_stat("offense", new_offense) 

    put_text(f"You've sold your {get_item_stat(item_id, 'weapons', 'item_name')} for {sell_price} gold.")
    put_text(f"Your offense is now {new_offense}.")
    put_buttons(["Continue"], onclick=[weapon_shop])
