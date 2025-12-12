# Red Dragon Rising Main Menu (Flask Version)

from flask import render_template, redirect, url_for

def main_menu_page():
    """
    Renders the main menu page.
    """
    return render_template("main_menu.html")

def exit_game_page():
    """
    Redirects to a goodbye page when the user chooses to exit.
    """
    return redirect(url_for('goodbye'))
