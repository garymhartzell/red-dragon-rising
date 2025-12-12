import webbrowser
from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
import os # For secret key generation

# Import page functions (will be converted to Flask blueprints or direct routes)
from src.main_menu import main_menu_page, exit_game_page
from src.new_game import new_game_page, create_character_post, handle_new_game_confirmation
from src.resume_game import resume_game_page
from src.town_square import town_square_page
from src.view_stats import view_stats_page

# Import blueprints
from routes.weapon_shop import weapon_shop_bp
from routes.bank import bank_bp

app = Flask(__name__)
# Generate a random secret key for session management
app.secret_key = os.urandom(24) 

# Register blueprints
app.register_blueprint(weapon_shop_bp)
app.register_blueprint(bank_bp)

@app.route('/')
@app.route('/main_menu')
def main_menu():
    return main_menu_page()

@app.route('/exit_game')
def exit_game():
    return exit_game_page()

@app.route('/goodbye')
def goodbye():
    return render_template('goodbye.html')

@app.route('/new_game')
def new_game():
    return new_game_page()

@app.route('/create_character', methods=['POST'])
def create_character():
    return create_character_post()

@app.route('/new_game/confirm', methods=['POST'])
def new_game_confirm():
    return handle_new_game_confirmation()

@app.route('/resume_game')
def resume_game():
    return resume_game_page()

@app.route('/town_square')
def town_square():
    return town_square_page()

@app.route('/view_stats')
def view_stats():
    return view_stats_page()



if __name__ == "__main__":
    # Open a browser window to the Flask app when the server starts
    webbrowser.open("http://127.0.0.1:8082/")
    app.run(debug=True, port=8082)
