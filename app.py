from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Mock recipe generator (replace with AI later)
def get_recipes(ingredients):
    return [
        f"{ingredients} Stir Fry",
        f"{ingredients} Pasta",
        f"{ingredients} Soup"
    ]

# Mock AI Ingredient Suggestion Function (does not have html/UI components yet)
def get_ingredients(user_input):
    """
    Returns a list of suggested ingredients based on user input.
    This is a mock function for testing purposes.
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

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Results page
@app.route("/results", methods=["POST"])
def results():
    ingredients = request.form.get("ingredients")
    recipes = get_recipes(ingredients)
    return render_template("results.html", recipes=recipes, ingredients=ingredients)

# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)