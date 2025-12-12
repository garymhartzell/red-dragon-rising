from flask import Blueprint, render_template, request, url_for, redirect

from src.bank import (
    bank, deposit_gold, withdraw_gold, deposit_gems, withdraw_gems,
    deposit_all, withdraw_all, open_gem_vault
)

bank_bp = Blueprint('bank_bp', __name__, url_prefix='/bank')

@bank_bp.route('/')
def bank_route():
    return bank()

@bank_bp.route('/deposit/gold', methods=['POST'])
def deposit_gold_route():
    return deposit_gold()

@bank_bp.route('/withdraw/gold', methods=['POST'])
def withdraw_gold_route():
    return withdraw_gold()

@bank_bp.route('/deposit/gems', methods=['POST'])
def deposit_gems_route():
    return deposit_gems()

@bank_bp.route('/withdraw/gems', methods=['POST'])
def withdraw_gems_route():
    return withdraw_gems()

@bank_bp.route('/deposit/all/gold', methods=['POST'])
def deposit_all_gold_route():
    return deposit_all('gold')

@bank_bp.route('/withdraw/all/gold', methods=['POST'])
def withdraw_all_gold_route():
    return withdraw_all('gold')

@bank_bp.route('/deposit/all/gems', methods=['POST'])
def deposit_all_gems_route():
    return deposit_all('gems')

@bank_bp.route('/withdraw/all/gems', methods=['POST'])
def withdraw_all_gems_route():
    return withdraw_all('gems')

@bank_bp.route('/open_gem_vault', methods=['POST'])
def open_gem_vault_route():
    return open_gem_vault()
