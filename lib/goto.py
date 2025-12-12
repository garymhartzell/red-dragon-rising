# goto() Navigation function for Red Dragon Rising (Flask version)

from flask import redirect, url_for
from lib.character import get_char_stat

def goto(location):
    """
    Handles navigation by redirecting to the specified Flask endpoint.
    The 'location' string should correspond to a registered Flask route name.
    """
    return redirect(url_for(location))

def goto_main_menu():
    """
    Handles returning the player to the main menu.
    """
    return redirect(url_for('main_menu'))

def go_back():
    """
    Redirects the player to their last recorded location.
    """
    back_to = get_char_stat("location")
    # If 'location' is not set or invalid, default to main_menu
    if not back_to:
        back_to = 'main_menu'
    return redirect(url_for(back_to))
    
