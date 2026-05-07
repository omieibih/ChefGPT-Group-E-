import json
import os

from flask import Blueprint, render_template, request
from groq import Groq


def get_recipes(
    ingredients: str,
    budget: str,
    experience_level: str = "Beginner",
    dietary_filter: str = "",
) -> list[dict]:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    budget_text = (
        f"The user has a budget of ${budget} to spend on additional ingredients."
        if budget
        else "The user has no specific budget — suggest affordable additions."
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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )

    return json.loads(response.choices[0].message.content.strip())


# --- Blueprint ---

recipes_bp = Blueprint("recipes", __name__)


@recipes_bp.route("/results", methods=["POST"])
def results():
    ingredients = request.form.get("ingredients", "")
    budget = request.form.get("budget", "").strip()
    experience_level = request.form.get("experience_level", "Beginner")
    dietary_filter = request.form.get("dietary_filter", "").strip()

    try:
        meals = get_recipes(ingredients, budget, experience_level, dietary_filter)
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
        dietary_filter=dietary_filter,
        error=error,
    )