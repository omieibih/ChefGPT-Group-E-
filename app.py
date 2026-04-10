from flask import Flask, render_template, request
import os

app = Flask(__name__)

# Mock recipe generator (replace with AI later)

# Choose experience level page
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ingredients", methods=["POST"])
def ingredients():
    experience = request.form.get("experience")
    return render_template("ingredients.html", experience=experience)

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