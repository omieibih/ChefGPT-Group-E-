"""
backend/routes/recipes.py
Handles AI-powered recipe generation.

Exports
-------
recipes_bp   – Flask Blueprint registered at app level
get_recipes  – pure function usable by tests or other modules
"""

# Used to convert the AI response (JSON string) into Python objects
import json

# Used to safely access environment variables like API keys
import os

# Flask imports:
# Blueprint -> organizes routes into modules
# render_template -> renders HTML pages
# request -> accesses incoming form data
from flask import Blueprint, render_template, request

# Groq SDK used to communicate with the Llama AI model
from groq import Groq

# Create a Flask Blueprint named "recipes"
# This allows these routes to be registered separately in the main app
recipes_bp = Blueprint("recipes", __name__)


# ---------------------------------------------------------------------------
# Core AI function
# ---------------------------------------------------------------------------

def get_recipes(
    ingredients: str, 
    budget: str, 
    experience_level: str = "Beginner",
    dietary_filter: str = "",
) -> list[dict]:
    """
    Calls the Groq/Llama API and returns a list of three meal dicts.

    Parameters
    ----------
    ingredients : str
        Comma-separated ingredients the user already has.
    budget : str
        Optional dollar amount the user can spend on extras.

    Returns
    -------
    list[dict]
        Each dict has keys: name, description, core_ingredients,
        additional_ingredients, instructions.
    """

    # Create a Groq client using the API key stored
    # in environment variables for security purposes
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Build a text string describing the user's budget
    # This gets inserted into the AI prompt later
    if budget:
        budget_text = (
            f"The user has a budget of ${budget} to spend on additional ingredients."
        )
    else:
        budget_text = (
            "The user has no specific budget — suggest affordable additions."
        )

    # Build instructions based on the user's cooking experience
    # This helps the AI tailor recipe complexity and explanations
    experience_text = (
        f"The user's cooking experience level is {experience_level}. "
        "Adjust the recipe instructions based on this level. "
        "For Beginner, use simple language, fewer steps, common tools, and avoid advanced techniques. "
        "For Intermediate, include moderate detail and basic cooking techniques. "
        "For Advanced, allow more complex techniques, timing details, and flavor-building steps."
    )

    # Main prompt sent to the AI model
    # Includes ingredients, budget, dietary restrictions,
    # and formatting instructions
    prompt = f"""You are a helpful chef assistant. The user has these ingredients on hand: {ingredients}.
{budget_text}
{experience_text}

Dietary restriction: {dietary_filter if dietary_filter else "none"}.

If a dietary restriction is provided, ONLY generate recipes that follow it.
Do NOT include ingredients that violate the dietary restriction.

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

    # Send the prompt to the Groq API using the Llama model
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        # Conversation format for the AI model
        messages=[{"role": "user", "content": prompt}],

        # Limits the maximum size of the AI response
        max_tokens=1500,
    )

    # The AI returns text, so convert the JSON string
    # into a real Python list of dictionaries
    return json.loads(response.choices[0].message.content.strip())


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

# Route that handles form submissions from the frontend
# Only accepts POST requests
@recipes_bp.route("/results", methods=["POST"])
def results():
    """Accepts the ingredient form and renders AI-generated meal suggestions."""

    # Get user input from the submitted form
    # Default values are provided in case fields are missing
    ingredients = request.form.get("ingredients", "")
    budget = request.form.get("budget", "").strip()
    experience_level = request.form.get("experience_level", "Beginner")
    dietary_filter = request.form.get("dietary_filter", "").strip()

    try:

        # First attempt to generate meals directly
        meals = get_recipes(ingredients, budget, experience_level, dietary_filter)

        # Import the main app module
        # This may be done to access another version/wrapper
        # of the get_recipes function
        import app as app_module

        # Generate recipes again using the function from app.py
        # This overwrites the previous meals variable
        meals = app_module.get_recipes(
            ingredients,
            budget,
            experience_level,
            dietary_filter,
        )

        # No error occurred
        error = None

    # If anything fails during recipe generation,
    # store the error message and return an empty meals list
    except Exception as exc:
        meals = []
        error = str(exc)

    # Render the results page and pass all variables
    # to the HTML template
    return render_template(
        "results.html",
        meals=meals,
        ingredients=ingredients,
        budget=budget,
        experience_level=experience_level,
        dietary_filter=dietary_filter,
        error=error,
    )