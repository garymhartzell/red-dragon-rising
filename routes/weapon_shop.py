from flask import Blueprint, render_template, request, url_for, redirect

from src.weapon_shop import (
    weapon_shop_page, 
    buy_weapon_page, 
    confirm_weapon_purchase_page, 
    finalize_weapon_purchase_post,
    sell_weapon_page,
    finalize_weapon_sale_post
)

weapon_shop_bp = Blueprint('weapon_shop_bp', __name__, url_prefix='/weapon_shop')

@weapon_shop_bp.route('/')
def weapon_shop():
    return weapon_shop_page()

@weapon_shop_bp.route('/buy')
def buy_weapon_page_route():
    return buy_weapon_page()

@weapon_shop_bp.route('/buy/<int:item_id>')
def confirm_weapon_purchase(item_id):
    return confirm_weapon_purchase_page(item_id)

@weapon_shop_bp.route('/buy/finalize', methods=['POST'])
def finalize_weapon_purchase():
    return finalize_weapon_purchase_post()

@weapon_shop_bp.route('/sell')
def sell_weapon_route():
    return sell_weapon_page()

@weapon_shop_bp.route('/sell/finalize', methods=['POST'])
def finalize_weapon_sale():
    return finalize_weapon_sale_post()
