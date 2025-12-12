# Red Dragon Rising Ye Old Bank

from flask import render_template, request, redirect, url_for, flash
from lib.character import get_char_stat, increment_char_stat, set_char_stat

def bank():
    """
    Renders the main bank page, displaying current gold and gem balances.
    """
    gold_on_hand = get_char_stat('gold_hand')
    gold_in_bank = get_char_stat('gold_bank')
    gems_on_hand = get_char_stat('gems_hand')
    gems_in_bank = get_char_stat('gems_bank')
    gem_vault_status = get_char_stat('gem_vault')

    return render_template(
        "bank.html",
        gold_on_hand=gold_on_hand,
        gold_in_bank=gold_in_bank,
        gems_on_hand=gems_on_hand,
        gems_in_bank=gems_in_bank,
        gem_vault_status=gem_vault_status
    )

def deposit_gold():
    """Handles depositing gold from hand to bank."""
    amount_str = request.form.get('amount')
    if not amount_str:
        flash("Please enter an amount to deposit.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    try:
        amount = int(amount_str)
    except ValueError:
        flash("Invalid amount. Please enter a number.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    gold_on_hand = get_char_stat('gold_hand')

    if amount <= 0:
        flash("Deposit amount must be positive.", "error")
    elif amount > gold_on_hand:
        flash(f"You only have {gold_on_hand} gold on hand.", "error")
    else:
        increment_char_stat('gold_hand', -amount)
        increment_char_stat('gold_bank', amount)
        flash(f"You have successfully deposited {amount} gold.", "success")
    return redirect(url_for('bank_bp.bank_route'))

def withdraw_gold():
    """Handles withdrawing gold from bank to hand."""
    amount_str = request.form.get('amount')
    if not amount_str:
        flash("Please enter an amount to withdraw.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    try:
        amount = int(amount_str)
    except ValueError:
        flash("Invalid amount. Please enter a number.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    gold_in_bank = get_char_stat('gold_bank')

    if amount <= 0:
        flash("Withdrawal amount must be positive.", "error")
    elif amount > gold_in_bank:
        flash(f"You only have {gold_in_bank} gold in the bank.", "error")
    else:
        increment_char_stat('gold_bank', -amount)
        increment_char_stat('gold_hand', amount)
        flash(f"You have successfully withdrawn {amount} gold.", "success")
    return redirect(url_for('bank_bp.bank_route'))

def deposit_gems():
    """Handles depositing gems from hand to bank."""
    amount_str = request.form.get('amount')
    if not amount_str:
        flash("Please enter an amount to deposit.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    try:
        amount = int(amount_str)
    except ValueError:
        flash("Invalid amount. Please enter a number.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    gems_on_hand = get_char_stat('gems_hand')

    if amount <= 0:
        flash("Deposit amount must be positive.", "error")
    elif amount > gems_on_hand:
        flash(f"You only have {gems_on_hand} gems on hand.", "error")
    else:
        increment_char_stat('gems_hand', -amount)
        increment_char_stat('gems_bank', amount)
        flash(f"You have successfully deposited {amount} gems.", "success")
    return redirect(url_for('bank_bp.bank_route'))

def withdraw_gems():
    """Handles withdrawing gems from bank to hand."""
    amount_str = request.form.get('amount')
    if not amount_str:
        flash("Please enter an amount to withdraw.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    try:
        amount = int(amount_str)
    except ValueError:
        flash("Invalid amount. Please enter a number.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    gems_in_bank = get_char_stat('gems_bank')

    if amount <= 0:
        flash("Withdrawal amount must be positive.", "error")
    elif amount > gems_in_bank:
        flash(f"You only have {gems_in_bank} gems in the bank.", "error")
    else:
        increment_char_stat('gems_bank', -amount)
        increment_char_stat('gems_hand', amount)
        flash(f"You have successfully withdrawn {amount} gems.", "success")
    return redirect(url_for('bank_bp.bank_route'))

def deposit_all(currency):
    """Handles depositing all of a currency from hand to bank."""
    if currency == 'gold':
        amount = get_char_stat('gold_hand')
        hand_key = 'gold_hand'
        bank_key = 'gold_bank'
    elif currency == 'gems':
        amount = get_char_stat('gems_hand')
        hand_key = 'gems_hand'
        bank_key = 'gems_bank'
    else:
        flash("Invalid currency.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    if amount > 0:
        increment_char_stat(hand_key, -amount)
        increment_char_stat(bank_key, amount)
        flash(f"You have successfully deposited all {amount} {currency}.", "success")
    else:
        flash(f"You have no {currency} on hand to deposit.", "warning")
    return redirect(url_for('bank_bp.bank_route'))

def withdraw_all(currency):
    """Handles withdrawing all of a currency from bank to hand."""
    if currency == 'gold':
        amount = get_char_stat('gold_bank')
        hand_key = 'gold_hand'
        bank_key = 'gold_bank'
    elif currency == 'gems':
        amount = get_char_stat('gems_bank')
        hand_key = 'gems_hand'
        bank_key = 'gems_bank'
    else:
        flash("Invalid currency.", "error")
        return redirect(url_for('bank_bp.bank_route'))

    if amount > 0:
        increment_char_stat(bank_key, -amount)
        increment_char_stat(hand_key, amount)
        flash(f"You have successfully withdrawn all {amount} {currency}.", "success")
    else:
        flash(f"You have no {currency} in the bank to withdraw.", "warning")
    return redirect(url_for('bank_bp.bank_route'))

def open_gem_vault():
    """Handles opening the gem vault."""
    if get_char_stat("gem_vault") == 0:
        # Cost to open gem vault (example: 100 gold)
        cost = 100
        gold_on_hand = get_char_stat('gold_hand')
        if gold_on_hand >= cost:
            increment_char_stat('gold_hand', -cost)
            set_char_stat("gem_vault", 1)
            flash(f"You've successfully opened a Gem Vault for {cost} gold! You can now store gems in the bank.", "success")
        else:
            flash(f"You need {cost} gold to open a Gem Vault. You only have {gold_on_hand} gold.", "error")
    else:
        flash("You already have a Gem Vault.", "info")
    return redirect(url_for('bank_bp.bank_route'))
