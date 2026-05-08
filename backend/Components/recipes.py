"""
recipes.py — Recipe Generation Feature

Overview:
    This file is the core feature of ChefGPT. It takes the user's ingredients,
    budget, experience level, and dietary filter, builds a prompt, sends it to
    an AI model, and renders the generated recipes on the results page.

How it works:
    1. The user fills out the ingredients form on templates/ingredients.html and
       submits it to /results.
    2. The results() route reads all the form fields and calls get_recipes().
    3. get_recipes() builds a natural-language prompt that includes the ingredients,
       budget instructions, experience level instructions, and any dietary restriction.
    4. The prompt is sent to the LLaMA 3.3 70B model via the Groq API.
    5. The model responds with a raw JSON array of exactly 3 meal suggestions.
    6. That JSON is parsed into a Python list and passed to templates/results.html
       for rendering.

Where data comes from:
    - ingredients:      Text input from the user (e.g. "chicken, rice, broccoli")
    - budget:           Optional number input — limits suggested extra ingredient costs
    - experience_level: Carried forward as a hidden form field from templates/ingredients.html
                        (originally chosen on the home page)
    - dietary_filter:   Optional text input (e.g. "vegan", "gluten-free")

What the AI returns (per meal):
    - name:                   Recipe name
    - description:            One-sentence description of the dish
    - core_ingredients:       List of ingredients the user already has
    - additional_ingredients: Extra ingredients to buy, with estimated prices
    - instructions:           Step-by-step cooking instructions (adjusted for experience level)

Files this feature interacts with:
    - templates/ingredients.html      — The form page that submits data to /results.
    - templates/results.html          — Renders the 3 generated meal cards. Also contains
                                        the "Save to Favorites" button that calls /api/favorites.
    - backend/Components/favorites.py — Handles saving a recipe after the user clicks
                                        "Save to Favorites" on the results page.
    - backend/Components/__init__.py  — Imports recipes_bp and registers it with the Flask app.
    - .env                            — Must contain GROQ_API_KEY for the Groq client to work.

Authentication:
    The /results route does not require authentication on the backend. Auth is handled
    client-side by JavaScript on the ingredients and results pages, which redirect to
    /login if no user is logged in.
"""

import json  # Used to parse the raw JSON string the AI model returns into a Python list
import os    # Used to read the GROQ_API_KEY from the environment (loaded from .env by app.py)

# Blueprint to group this file's routes,
# render_template to serve the results HTML page,
# request to read the form fields submitted by the user
from flask import Blueprint, render_template, request

# Groq is the API client used to send prompts to the LLaMA model and receive responses
from groq import Groq


def get_recipes(
    ingredients: str,        # Comma-separated string of ingredients the user has on hand
    budget: str,             # Dollar amount as a string, or empty string if no budget
    experience_level: str = "Beginner",   # One of: "Beginner", "Intermediate", "Advanced"
    dietary_filter: str = "",             # Free-text restriction like "vegan" or "gluten-free"
) -> list[dict]:             # Returns a list of 3 meal dicts parsed from the AI's JSON response
    # Initialize the Groq API client using the key stored in environment variables
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    # Build the budget portion of the prompt.
    # If the user provided a budget, tell the AI to respect it;
    # otherwise instruct it to suggest affordable additions.
    budget_text = (
        f"The user has a budget of ${budget} to spend on additional ingredients."
        if budget
        else "The user has no specific budget — suggest affordable additions."
    )

    # Build the experience level portion of the prompt.
    # This tells the AI how complex the recipe instructions should be.
    experience_text = (
        f"The user's cooking experience level is {experience_level}. "
        "Adjust the recipe instructions based on this level. "
        "For Beginner, use simple language, fewer steps, common tools, and avoid advanced techniques. "
        "For Intermediate, include moderate detail and basic cooking techniques. "
        "For Advanced, allow more complex techniques, timing details, and flavor-building steps."
    )

    # Combine all inputs into a single natural-language prompt.
    # The AI is instructed to return ONLY a raw JSON array so we can parse it directly.
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

    # Send the assembled prompt to the LLaMA 3.3 70B model via the Groq API.
    # max_tokens caps the response length to prevent excessively long or runaway output.
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # The specific AI model to use
        messages=[{"role": "user", "content": prompt}],  # The prompt sent as a user message
        max_tokens=1500,                   # Limit response to ~1500 tokens
    )

    # Extract the text content from the response, strip any surrounding whitespace,
    # and parse it from a JSON string into a Python list of meal dicts
    return json.loads(response.choices[0].message.content.strip())


# --- Blueprint ---

# Create the Blueprint — Flask registers all routes defined below when
# app.py calls app.register_blueprint() via backend/Components/__init__.py
recipes_bp = Blueprint("recipes", __name__)


# Route: POST /results
# Called when the user submits the ingredients form on templates/ingredients.html.
# Generates recipes via the AI and renders them on the results page.
@recipes_bp.route("/results", methods=["POST"])
def results():
    # Read the ingredients the user typed in (e.g. "chicken, rice, broccoli")
    ingredients = request.form.get("ingredients", "")

    # Read the optional budget and strip any accidental whitespace
    budget = request.form.get("budget", "").strip()

    # Read the experience level carried forward as a hidden field from the ingredients page
    # Defaults to "Beginner" if somehow missing
    experience_level = request.form.get("experience_level", "Beginner")

    # Read the optional dietary filter and strip whitespace (e.g. "vegan", "gluten-free")
    dietary_filter = request.form.get("dietary_filter", "").strip()

    try:
        # Call the AI recipe generator with all four inputs
        meals = get_recipes(ingredients, budget, experience_level, dietary_filter)
        # No error occurred — set error to None so the template knows not to show an error message
        error = None
    except Exception as exc:
        # If the AI call fails (e.g. invalid API key, network error, malformed JSON response),
        # render the page with an empty meal list and display the error message instead
        meals = []
        error = str(exc)

    # Render the results page, passing:
    # - meals: the list of 3 generated meal dicts (empty list on error)
    # - ingredients, budget, experience_level, dietary_filter: echoed back for display
    # - error: None on success, or an error string to show the user what went wrong
    return render_template(
        "results.html",
        meals=meals,
        ingredients=ingredients,
        budget=budget,
        experience_level=experience_level,
        dietary_filter=dietary_filter,
        error=error,
    )
