# Red Dragon Rising Town Square (Flask Version)

from flask import render_template, redirect, url_for
from lib.character import set_char_stat

def town_square_page():
    """
    Renders the town square page.
    """
    set_char_stat("location", "town_square") # Keep track of player's location
    return render_template("town_square.html")
        
