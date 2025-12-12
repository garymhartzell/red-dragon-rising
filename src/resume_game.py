# Resume Game for Red Dragon Rising (Flask Version)

from flask import render_template, redirect, url_for
from lib.character import get_char_stat

def resume_game_page():
    """
    Renders the resume game page, checking character status.
    """
    if get_char_stat("awake") == "dead":
        message = "You are alive again."
        return render_template("resume_game.html", message=message, next_action=url_for('main_menu'))
    elif get_char_stat("status") == "asleep_inn":
        message = "You are sleeping at the Knight Fall Inn."
        return render_template("resume_game.html", message=message, next_action=url_for('main_menu'))
    else: 
        return redirect(url_for('town_square'))
    
