"""
app.py
Application entry point.

Responsibilities
----------------
- Create the Flask app instance
- Load environment variables
- Register all feature blueprints
- Start the dev server when run directly

All business logic lives in backend/routes/*.py and backend/*.py.
"""

import os

from dotenv import load_dotenv
from flask import Flask

# Load .env before any other import that reads env vars.
load_dotenv()

# Firebase is initialised as a side-effect of this import so it happens once,
# before any blueprint tries to use it.
import backend.firebase_init  # noqa: F401

from backend.routes import all_blueprints

app = Flask(__name__)

for blueprint in all_blueprints:
    app.register_blueprint(blueprint)


# -----------------------------------------------
# Mock ingredient suggester (used by test cases)
# -----------------------------------------------
def get_ingredients(user_input):
    """
    Returns a list of suggested ingredients based on user input.
    Mock function used for unit testing purposes.
    """
    user_input = user_input.lower().strip()

    if "high protein" in user_input:
        return ["chicken", "eggs", "greek yogurt", "beans"]
    elif "cheap" in user_input:
        return ["rice", "pasta", "potatoes", "canned tuna"]
    elif "vegan" in user_input:
        return ["tofu", "lentils", "quinoa", "spinach"]
    elif user_input == "":
        return ["Please enter a request."]
    else:
        return ["tomatoes", "onions", "garlic", "chicken"]


# -----------------------------------------------
# Mock nutrition breakdown (used by test cases)
# -----------------------------------------------
def get_nutrition(food_name):
    """
    Returns a nutrition breakdown for a given food.
    Mock function used for unit testing purposes.
    """
    food_name = food_name.lower().strip()

    if not food_name:
        return "Please enter a food name."

    nutrition_data = {
        "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fat": 0.3},
        "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fat": 0.4},
        "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "rice": {"calories": 206, "protein": 4.3, "carbs": 45, "fat": 0.4},
        "egg": {"calories": 78, "protein": 6, "carbs": 0.6, "fat": 5},
    }

    if food_name in nutrition_data:
        return nutrition_data[food_name]

    return "Food not found."


# -----------------------------------------------
# In-memory favorites (used by test cases)
# -----------------------------------------------
_favorites = []

def save_recipe(name):
    if name == "":
        return "Please enter a recipe name."
    if name in _favorites:
        return True
    _favorites.append(name)
    return True

def get_favorites_local():
    return _favorites

def remove_recipe(name):
    if name in _favorites:
        _favorites.remove(name)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
