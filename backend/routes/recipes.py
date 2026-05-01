"""
backend/routes/recipes.py
Handles AI-powered recipe generation.

Exports
-------
recipes_bp   – Flask Blueprint registered at app level
get_recipes  – pure function usable by tests or other modules
"""

import json
import os

from flask import Blueprint, render_template, request
from groq import Groq

recipes_bp = Blueprint("recipes", __name__)

#---------------------------------------------------------------------------
# Adds experience level route
#---------------------------------------------------------------------------

@recipes_bp.route("/ingredients", methods=["POST"])
def ingredients():
    """Receives experience level and shows the ingredients page."""

    experience_level = request.form.get("experience_level", "Beginner")

    return render_template(
        "ingredients.html",
        experience_level=experience_level
    )



# ---------------------------------------------------------------------------
# Core AI function
# ---------------------------------------------------------------------------

def get_recipes(ingredients: str, budget: str, experience_level: str = "Beginner") -> list[dict]:
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
    # API key comes from the environment to avoid CWE-798.
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    if budget:
        budget_text = (
            f"The user has a budget of ${budget} to spend on additional ingredients."
        )
    else:
        budget_text = (
            "The user has no specific budget — suggest affordable additions."
        )

    prompt = f"""You are a helpful chef assistant. The user has these ingredients on hand: {ingredients}.
{budget_text}

The user's cooking experience level is: {experience_level}.
Adjust the recipe difficulty accordingly.

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


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@recipes_bp.route("/results", methods=["POST"])
def results():
    """Accepts the ingredient form and renders AI-generated meal suggestions."""
    ingredients = request.form.get("ingredients", "")
    budget = request.form.get("budget", "").strip()

    # Adds Experience Level Feature 
    experience_level = request.form.get("experience_level", "Beginner")
    try:
        meals = get_recipes(ingredients, budget, experience_level)
        error = None
    except Exception as exc:
        meals = []
        error = str(exc)

    return render_template(
        "results.html",
        meals=meals,
        ingredients=ingredients,
        budget=budget,
        experience_level=experience_level,
        error=error,
    )