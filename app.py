from flask import Flask, render_template, request
import os

from backend.experience_filter import get_recipes

app = Flask(__name__)

# Mock recipe generator (replace with AI later)

# Choose experience level page
@app.route("/")
def home():
    return render_template("index.html")

# Ingredients input page with budget
@app.route("/ingredients", methods=["POST"])
def ingredients():
    experience = request.form.get("experience")
    return render_template("ingredients.html", experience=experience)

# Results page
@app.route("/results", methods=["POST"])
def results():
    ingredients = request.form.get("ingredients", "").strip()
    budget = request.form.get("budget", "").strip()
    experience_level = request.form.get("experience_level", "beginner").strip().lower()

    print("DEBUG ingredients:", ingredients)
    print("DEBUG budget:", budget)
    print("DEBUG experience_level:", experience_level)

    if not ingredients:
        return render_template(
            "ingredients.html",
            experience_level=experience_level,
            error="Please enter at least one ingredient.",
        )

    try:
        meals = get_recipes(ingredients, budget, experience_level)
        print("DEBUG meals:", meals)
    except Exception as e:
        print("DEBUG error:", e)
        return render_template(
            "results.html",
            meals=[],
            ingredients=ingredients,
            budget=budget,
            experience_level=experience_level,
            error=str(e),
        )

    return render_template(
        "results.html",
        meals=meals,
        ingredients=ingredients,
        budget=budget,
        experience_level=experience_level,
        error=None,
    )
# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)