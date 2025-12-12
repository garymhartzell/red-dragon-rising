# New Game - Character Creation (Flask Version)

from flask import render_template, request, redirect, url_for, flash
from lib.character import set_char_stat, ensure_character_file, CHAR_FILE
import os

def new_game_page():
    """
    Renders the new game character creation page.
    Checks if a character file exists and prompts the user.
    """
    # Check if character.json exists
    char_file_path = os.path.join("assets", "character.json")
    if os.path.exists(char_file_path):
        return render_template("new_game/confirm.html")
            
    return render_template("new_game/main.html")

def create_character_post():
    """
    Handles the POST request for character creation.
    """
    name = request.form.get("name")
    gender = request.form.get("gender")
    specialty = request.form.get("specialty")

    if not name:
        flash("Warning: You must enter a name!", "error")
        return redirect(url_for('new_game')) # Redirect back to the form

    # Ensure character file exists (or create a new one if confirmed)
    ensure_character_file() # This will create an empty character.json if it doesn't exist

    set_char_stat("name", name)
    set_char_stat("gender", gender)
    set_char_stat("specialty", specialty)
    set_char_stat("xp", 1)
    set_char_stat("level", 1)
    set_char_stat("rank", "Apprentice")
    set_char_stat("max_hp", 25)
    set_char_stat("hp", 25)
    set_char_stat("offense", 10)
    set_char_stat("defense", 10)
    set_char_stat("stamina", 0)
    set_char_stat("charm", 0)
    set_char_stat("gold_hand", 50)
    set_char_stat("gold_bank", 0)
    set_char_stat("gems_hand", 0)
    set_char_stat("gems_bank", 0)
    set_char_stat("weapon_id", 0)
    set_char_stat("armor_id", 0)
    set_char_stat("horse_id", 0)
    set_char_stat("status", "awake")
    set_char_stat("healing_potions", 1)
    set_char_stat("killed", 0)
    set_char_stat("kills", 0)
    
    flash(f"Character Created! Welcome, {name}.", "success")
    return render_template("new_game/success.html", name=name)

def handle_new_game_confirmation():
    """
    Handles the confirmation to start a new game, deleting existing character data.
    """
    # Delete the existing character file
    if os.path.exists(CHAR_FILE):
        try:
            os.remove(CHAR_FILE)
            flash("Previous character data deleted. Starting a new game.", "info")
        except OSError as e:
            flash(f"Error deleting previous character data: {e}", "error")
    else:
        flash("No existing character data found to delete.", "warning")
    
    # Redirect to the new game creation page (which will now show the form)
    return redirect(url_for('new_game'))

        
