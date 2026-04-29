from flask import Flask, render_template, request, jsonify
import os
import json
from groq import Groq

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
try:
    from groq import Groq
except Exception:
    Groq = None

from backend.favorites import save_favorite, get_favorites, delete_favorite
from backend.ingredient_suggestions import generate_ingredient_suggestions


# Security note: keep Firebase service-account secrets out of source control.
# We will load credentials from environment or a local ignored file to address
# CWE-798 (Use of Hard-coded Credentials).
def _load_firebase_credentials():
    """Load Firebase Admin credentials from env vars or local fallback file."""
    key_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if key_json:
        return credentials.Certificate(json.loads(key_json))

    key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    if os.path.exists(key_path):
        return credentials.Certificate(key_path)

    raise RuntimeError(
        "Firebase credentials not found. Set FIREBASE_SERVICE_ACCOUNT_JSON or "
        "FIREBASE_SERVICE_ACCOUNT_PATH."
    )


# Initialize Firebase Admin SDK once, but do not crash local development if
# credentials are not configured yet.
FIREBASE_AVAILABLE = True
FIREBASE_INIT_ERROR = None
if not firebase_admin._apps:
    try:
        firebase_admin.initialize_app(_load_firebase_credentials())
    except Exception as e:
        FIREBASE_AVAILABLE = False
        FIREBASE_INIT_ERROR = str(e)

app = Flask(__name__)


# -----------------------------------------------
# Auth middleware helper
# -----------------------------------------------
def get_current_user(request):
    """Verifies Firebase ID token from Authorization header."""
    if not FIREBASE_AVAILABLE:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
        return decoded
    except Exception:
        return None


# -----------------------------------------------
# AI-powered recipe generator (used by main app)
# -----------------------------------------------
def get_recipes(ingredients, budget):

    from groq import Groq

    # Security note: API keys must come from environment variables, not literals,
    # to avoid CWE-798 (Use of Hard-coded Credentials).
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

def remove_recipe(name):
    if name in _favorites:
        _favorites.remove(name)


# -----------------------------------------------
# Routes
# -----------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/favorites")
def favorites_page():
    return render_template("favorites.html")


@app.route("/results", methods=["POST"])
def results():
    ingredients = request.form.get("ingredients")
    budget = request.form.get("budget", "").strip()
    try:
        meals = get_recipes(ingredients, budget)
    except Exception as e:
        return render_template("results.html", meals=[], ingredients=ingredients, budget=budget, error=str(e))
    return render_template("results.html", meals=meals, ingredients=ingredients, budget=budget, error=None)


# Favorites API
@app.route("/api/favorites", methods=["POST"])
def api_save_favorite():
    if not FIREBASE_AVAILABLE:
        return jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}), 503

    # Verify user identity from Firebase token in Authorization header.
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Save one favorite recipe document for this user.
    firestore_save_favorite(user, request.get_json())
    return jsonify({"message": "Saved!"}), 200


@app.route("/api/favorites", methods=["GET"])
def api_get_favorites():
    if not FIREBASE_AVAILABLE:
        return jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}), 503

    # Verify user identity.
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Return all favorites owned by this user.
    return jsonify(get_favorites(user)), 200


@app.route("/api/favorites/<doc_id>", methods=["DELETE"])
def api_delete_favorite(doc_id):
    if not FIREBASE_AVAILABLE:
        return jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}), 503

    # Verify user identity.
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Delete one favorite by Firestore document id.
    delete_favorite(doc_id)
    return jsonify({"message": "Deleted"}), 200


# Ingredient suggestions API
@app.route("/api/ingredient-suggestions", methods=["GET"])
def api_ingredient_suggestions():
    # Verify the caller is logged in.
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Load this user's saved favorite recipes.
    favorites = get_favorites(user)

    # Turn one favorite recipe into a small set of ingredient chips.
    data = generate_ingredient_suggestions(user, favorites)

    # Send JSON back to the floating assistant card.
    return jsonify(data), 200


# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)