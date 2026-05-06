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

import json
import os

from dotenv import load_dotenv
from flask import Flask
from groq import Groq

# Load .env before any other import that reads env vars.
load_dotenv()

# Firebase is initialised as a side-effect of this import so it happens once,
# before any blueprint tries to use it.
import backend.firebase_init  # noqa: F401

from backend.routes import all_blueprints

app = Flask(__name__)

for blueprint in all_blueprints:
    app.register_blueprint(blueprint)


def get_recipes(ingredients, budget, experience_level="Beginner"):
    """Compatibility helper used by existing unit tests."""
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    if budget:
        budget_text = (
            f"The user has a budget of ${budget} to spend on additional ingredients."
        )
    else:
        budget_text = (
            "The user has no specific budget — suggest affordable additions."
        )

    experience_text = (
        f"The user's cooking experience level is {experience_level}. "
        "Adjust the recipe instructions based on this level. "
        "For Beginner, use simple language, fewer steps, common tools, and avoid advanced techniques. "
        "For Intermediate, include moderate detail and basic cooking techniques. "
        "For Advanced, allow more complex techniques, timing details, and flavor-building steps."
    )

    prompt = f"""You are a helpful chef assistant. The user has these ingredients on hand: {ingredients}.
{budget_text}
{experience_text}

Suggest exactly 3 different meals where the provided ingredients are the heart/star of the dish.
For each meal, suggest any additional ingredients they may need to buy to complete the recipe, keeping the budget in mind if one was provided.

Respond ONLY with a raw JSON array — no markdown, no code fences, no explanation. Use this exact structure:
[
  {{
    "name": "Meal Name",
    "description": "A one-sentence description of the dish.",
    "core_ingredients": ["ingredient1", "ingredient2"],
    "additional_ingredients": ["extra ingredient (~$price)", "extra ingredient (~$price)"],
    "instructions": [
      "Step 1: ...",
      "Step 2: ...",
      "Step 3: ..."
    ]
  }}
]"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )

    return json.loads(response.choices[0].message.content.strip())


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


def get_favorites():
    """Compatibility alias used by some test modules."""
    return get_favorites_local()

def remove_recipe(name):
    if name in _favorites:
        _favorites.remove(name)

from backend.routes.nutrition_route import nutrition_bp
app.register_blueprint(nutrition_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
