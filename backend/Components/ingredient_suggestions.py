import random
import re

from flask import Blueprint, jsonify, request

from backend.Core.auth_helper import get_current_user
from backend.Components.favorites import get_favorites

DEFAULT_INGREDIENTS = ["garlic", "onion", "rice", "tomato", "eggs", "beans"]

TITLE_HINTS = [
    ("parmesan", ["pasta", "tomato", "cheese", "garlic", "basil"]),
    ("pasta", ["tomato", "cheese", "garlic", "basil"]),
    ("spaghetti", ["tomato", "cheese", "garlic", "basil"]),
    ("pizza", ["dough", "tomato", "cheese", "pepperoni"]),
    ("taco", ["tortillas", "tomato", "cheese", "onion", "salsa"]),
    ("salad", ["lettuce", "tomato", "cucumber", "olive oil"]),
    ("stir fry", ["rice", "soy sauce", "broccoli", "garlic"]),
    ("curry", ["rice", "coconut milk", "garlic", "ginger"]),
    ("soup", ["broth", "carrot", "onion", "celery"]),
    ("burger", ["bun", "lettuce", "tomato", "cheese"]),
]


def _extract_ingredients(raw_ingredients):
    ingredients = []
    seen = set()
    for part in re.split(r"[,;/\n]+", str(raw_ingredients)):
        item = re.sub(r"\s*\([^)]*\)\s*$", "", part).strip()
        if not item:
            continue
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        ingredients.append(item)
    return ingredients


def _title_based_ingredients(title):
    normalized_title = str(title).lower()
    hints = []
    for keyword, candidates in TITLE_HINTS:
        if keyword in normalized_title:
            for candidate in candidates:
                if candidate not in hints:
                    hints.append(candidate)
    return hints


def generate_ingredient_suggestions(user, favorites, limit=8):
    if not favorites:
        return {
            "recipe_title": "",
            "suggested_ingredients": DEFAULT_INGREDIENTS[:3],
            "no_favorites": True,
        }

    recipe = random.choice(favorites)
    ingredients = _extract_ingredients(recipe.get("ingredients", ""))

    for item in _title_based_ingredients(recipe.get("name", "")):
        if item.lower() not in {existing.lower() for existing in ingredients}:
            ingredients.append(item)

    if len(ingredients) < min(limit, 3):
        existing = {item.lower() for item in ingredients}
        for fallback in DEFAULT_INGREDIENTS:
            if fallback not in existing:
                ingredients.append(fallback)
            if len(ingredients) >= min(limit, 3):
                break

    return {
        "recipe_title": recipe.get("name", "a recipe you liked"),
        "suggested_ingredients": ingredients[:limit],
        "no_favorites": False,
    }


# --- Blueprint ---

ingredients_bp = Blueprint("ingredients", __name__, url_prefix="/api")


@ingredients_bp.route("/ingredient-suggestions", methods=["GET"])
def api_ingredient_suggestions():
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    favorites = get_favorites(user)
    data = generate_ingredient_suggestions(user, favorites)
    return jsonify(data), 200