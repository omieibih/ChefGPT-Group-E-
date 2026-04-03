from flask import Flask, render_template, request
import os
import json
from groq import Groq

app = Flask(__name__)


# -----------------------------------------------
# AI-powered recipe generator (used by main app)
# -----------------------------------------------
def get_recipes(ingredients, budget):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    budget_text = f"The user has a budget of ${budget} to spend on additional ingredients." if budget else "The user has no specific budget — suggest affordable additions."

    prompt = f"""You are a helpful chef assistant. The user has these ingredients on hand: {ingredients}.
{budget_text}

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
        max_tokens=1500
    )

    meals = json.loads(response.choices[0].message.content.strip())
    return meals


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
# Routes
# -----------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/results", methods=["POST"])
def results():
    ingredients = request.form.get("ingredients")
    budget = request.form.get("budget", "").strip()
    try:
        meals = get_recipes(ingredients, budget)
    except Exception as e:
        return render_template("results.html", meals=[], ingredients=ingredients, budget=budget, error=str(e))
    return render_template("results.html", meals=meals, ingredients=ingredients, budget=budget, error=None)


# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)