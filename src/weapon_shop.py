# Red Dragon Rising Weapon Shop (Flask Version)

from flask import render_template, redirect, url_for, flash, request
from lib.character import set_char_stat, get_char_stat
from lib.items import get_item_stat, get_available_items
import random

def weapon_shop_page():
    """
    Renders the main weapon shop page.
    """
    set_char_stat("location", "weapon_shop")
    gold_hand = get_char_stat("gold_hand")
    return render_template("weapon_shop/main.html", gold_hand=gold_hand)

def buy_weapon_page():
    """
    Displays weapons available for purchase.
    """
    current_weapon_id = int(get_char_stat("weapon_id"))
    if 101 <= current_weapon_id <= 199:
        weapon_name = get_item_stat(current_weapon_id, "weapons", "item_name")
        flash(f'The shopkeeper looks you over and says, "You already have a weapon. Would you like to sell your {weapon_name} first?"', "info")
        return redirect(url_for('weapon_shop_bp.sell_weapon_route'))
    
    player_level = get_char_stat("level")  
    weapons = get_available_items("weapons", player_level)
    return render_template("weapon_shop/buy.html", weapons=weapons)

def confirm_weapon_purchase_page(item_id):
    """
    Confirms the purchase of a specific weapon.
    """
    weapon_name = get_item_stat(item_id, "weapons", "item_name")
    weapon_price = get_item_stat(item_id, "weapons", "cost")
    return render_template("weapon_shop/confirm_buy.html", item_id=item_id, weapon_name=weapon_name, weapon_price=weapon_price)

def finalize_weapon_purchase_post():
    """
    Handles the POST request to finalize a weapon purchase.
    """
    item_id = int(request.form.get('item_id'))
    gold_hand = get_char_stat("gold_hand")
    weapon_price = get_item_stat(item_id, "weapons", "cost")
    weapon_boost = get_item_stat(item_id, "weapons", "boost")  
    char_offense = get_char_stat("offense")

    if gold_hand < weapon_price:
        flash("You don't have enough gold to buy this weapon.", "error")
        return redirect(url_for('buy_weapon_page'))

    set_char_stat("gold_hand", gold_hand - weapon_price)
    set_char_stat("weapon_id", item_id)
    set_char_stat("offense", char_offense + weapon_boost)
    
    flash(f"You have purchased a {get_item_stat(item_id, 'weapons', 'item_name')}!", "success")
    return redirect(url_for('weapon_shop_bp.weapon_shop'))

def sell_weapon_page():
    """
    Displays the current weapon and prompts to sell it.
    """
    current_weapon_id = int(get_char_stat("weapon_id"))

    if not (101 <= current_weapon_id <= 199):
        flash("You don't have a weapon to sell.", "info")
        return redirect(url_for('weapon_shop'))

    weapon_name = get_item_stat(current_weapon_id, "weapons", "item_name")
    sell_min = get_item_stat(current_weapon_id, "weapons", "sell_min")
    sell_max = get_item_stat(current_weapon_id, "weapons", "sell_max")
    sell_price = random.randint(sell_min, sell_max) # Randomized selling price

    return render_template("weapon_shop/sell.html", weapon_name=weapon_name, sell_price=sell_price, item_id=current_weapon_id)

def finalize_weapon_sale_post():
    """
    Handles the POST request to finalize a weapon sale.
    """
    item_id = int(request.form.get('item_id'))
    sell_price = int(request.form.get('sell_price')) # Get the price from the form
    
    gold_hand = get_char_stat("gold_hand")
    char_offense = get_char_stat("offense")
    weapon_boost = get_item_stat(item_id, "weapons", "boost")

    new_offense = max(0, char_offense - weapon_boost)

    set_char_stat("gold_hand", gold_hand + sell_price)
    set_char_stat("weapon_id", 0) 
    set_char_stat("offense", new_offense) 

    flash(f"You've sold your {get_item_stat(item_id, 'weapons', 'item_name')} for {sell_price} gold. Your offense is now {new_offense}.", "success")
    return redirect(url_for('weapon_shop_bp.weapon_shop'))
