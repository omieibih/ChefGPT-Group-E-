from flask import Flask, render_template, request
import os
import json
from groq import Groq

app = Flask(__name__)

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)