"""
backend/routes/ingredients.py
API endpoint that returns personalised ingredient suggestion chips for the
floating assistant panel on the home page.

The endpoint requires authentication so suggestions can be tailored to the
user's saved favourite recipes.
"""

from flask import Blueprint, jsonify, request

from backend.auth_helper import get_current_user
from backend.favorites import get_favorites
from backend.ingredient_suggestions import generate_ingredient_suggestions

ingredients_bp = Blueprint("ingredients", __name__, url_prefix="/api")


@ingredients_bp.route("/ingredient-suggestions", methods=["GET"])
def api_ingredient_suggestions():
    """
    Returns a small set of ingredient suggestion chips derived from the
    authenticated user's saved favourite recipes.

    Response shape (mirrors generate_ingredient_suggestions):
        {
            "message": "...",
            "chips":   ["ingredient1", "ingredient2", ...]
        }
    """
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    favorites = get_favorites(user)
    data = generate_ingredient_suggestions(user, favorites)
    return jsonify(data), 200