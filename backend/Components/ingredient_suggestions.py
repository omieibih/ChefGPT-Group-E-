"""
ingredient_suggestions.py — Ingredient suggestion helper

Overview:
    Provides a small API that suggests ingredients to the user based on their
    saved favorites and the recipe titles. The goal is lightweight, reliable
    suggestions (not a recommender system). This module focuses on safety,
    simplicity, and clear separation of concerns:

    - auth is delegated to `backend.Core.auth_helper.get_current_user` (no token
      parsing in this file)
    - favorites are read via `backend.Components.favorites.get_favorites`
    - suggestion logic is encapsulated in small, well-tested helper functions

Security & Reliability notes included inline:
    - Authentication: API route requires a logged-in user (returns 401 otherwise).
    - Input sanitization: ingredient extraction normalizes and strips inputs and
      removes parenthetical annotations (e.g. "tomato (diced)").
    - Deduplication: suggestions are de-duplicated (case-insensitive).
    - Fallbacks: when favorites are empty or extraction yields few items, the
      module falls back to `DEFAULT_INGREDIENTS` to ensure a useful response.

Architecture:
    - Pure helper functions perform parsing and hint generation.
    - A small Flask Blueprint exposes the HTTP endpoint under `/api/ingredient-suggestions`.
    - This keeps web concerns (request/response) separate from algorithmic logic.

"""

import random
import re

from flask import Blueprint, jsonify, request

from backend.Core.auth_helper import get_current_user
from backend.Components.favorites import get_favorites

# Defaults and configuration -------------------------------------------------
# A small list of sensible fallback ingredients used when favorites are empty
# or when extraction doesn't provide enough items. Chosen to be broadly useful.
DEFAULT_INGREDIENTS = ["garlic", "onion", "rice", "tomato", "eggs", "beans"]

# Title-based hint table: if a saved recipe's title contains any of these
# keywords we add domain-appropriate candidate ingredients. This is a cheap
# heuristic to improve suggestions without model calls or external services.
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


# Parsing helpers --------------------------------------------------------------
def _extract_ingredients(raw_ingredients):
    """
    Normalize a raw ingredient string into a deduplicated list.

    - Splits on common separators (comma, semicolon, slash, newline).
    - Removes trailing parenthetical notes like "(diced)" which are not
      useful for high-level ingredient suggestions.
    - Preserves the user's original casing for display but deduplicates using
      a case-insensitive key.

    This function is defensive: it accepts any input and will always return
    a list (possibly empty), which makes the caller simpler and more robust.
    """
    ingredients = []
    seen = set()
    # Convert to string to avoid crashes if the field is None or a list
    for part in re.split(r"[,;/\n]+", str(raw_ingredients)):
        # Remove parenthetical annotations (e.g. "tomato (diced)") and trim
        item = re.sub(r"\s*\([^)]*\)\s*$", "", part).strip()
        if not item:
            continue
        key = item.lower()
        # Deduplicate case-insensitively while preserving first-seen casing
        if key in seen:
            continue
        seen.add(key)
        ingredients.append(item)
    return ingredients


def _title_based_ingredients(title):
    """
    Return a short list of hint ingredients based on keywords found in `title`.

    This is an intentionally simple heuristic: we do a substring check against
    TITLE_HINTS and append candidates that are not already present. Keep it
    deterministic and fast to maintain reliability.
    """
    normalized_title = str(title).lower()
    hints = []
    for keyword, candidates in TITLE_HINTS:
        if keyword in normalized_title:
            for candidate in candidates:
                if candidate not in hints:
                    hints.append(candidate)
    return hints


def generate_ingredient_suggestions(user, favorites, limit=8):
    """
    Main suggestion algorithm.

    Inputs:
        - `user`: decoded user object from auth (not used directly here but kept
           for future personalization hooks and for clearer calling semantics).
        - `favorites`: list of favorite recipe dicts (as returned by get_favorites).
        - `limit`: maximum number of suggestions to return.

    Returns a dict with keys:
        - `recipe_title`: human-friendly title used as the suggestion context.
        - `suggested_ingredients`: list of ingredient strings (length <= limit).
        - `no_favorites`: boolean flag the frontend can use to alter UI.

    Reliability measures:
        - If the user has no favorites, return a small, useful fallback set.
        - Always ensure the returned list is deduplicated and capped by `limit`.
    """
    # If the user has no favorites, return a short fallback so the UI can still
    # show something helpful. This avoids exposing implementation details and
    # prevents errors in the frontend when an empty list would be surprising.
    if not favorites:
        return {
            "recipe_title": "",
            "suggested_ingredients": DEFAULT_INGREDIENTS[:3],
            "no_favorites": True,
        }

    # Pick one saved favorite at random to provide variety across calls.
    recipe = random.choice(favorites)

    # Extract ingredients from the saved recipe's `ingredients` field. We pass
    # a default of "" to be defensive in case the payload is malformed.
    ingredients = _extract_ingredients(recipe.get("ingredients", ""))

    # Add title-based hints (if any) but only if they aren't already present.
    for item in _title_based_ingredients(recipe.get("name", "")):
        if item.lower() not in {existing.lower() for existing in ingredients}:
            ingredients.append(item)

    # Ensure we have at least a small number of suggestions: add fallbacks from
    # DEFAULT_INGREDIENTS while preserving uniqueness.
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


# --- Flask Blueprint (HTTP layer) -------------------------------------------
# The blueprint maps HTTP requests to the small, well-tested helpers above. By
# keeping request handling here minimal we keep authentication and web concerns
# separate from the suggestion logic.
ingredients_bp = Blueprint("ingredients", __name__, url_prefix="/api")


@ingredients_bp.route("/ingredient-suggestions", methods=["GET"])
def api_ingredient_suggestions():
    """
    HTTP GET /api/ingredient-suggestions

    Behavior and security:
      - Validates the requesting user via `get_current_user(request)`. If no
        user is present, responds with 401 to avoid leaking any personalized
        information.
      - Fetches the user's favorites and delegates to `generate_ingredient_suggestions`.
      - Always returns JSON and an explicit HTTP status code.
    """
    # Authentication: get_current_user reads the Authorization header and
    # returns the decoded user or None. This file does not parse tokens itself
    # which reduces duplicated auth logic across the codebase.
    user = get_current_user(request)
    if not user:
        # 401 prevents any user-specific data from leaking to anonymous clients
        return jsonify({"error": "Unauthorized"}), 401

    # Read favorites (database call lives inside the favorites component).
    favorites = get_favorites(user)

    # Core logic is pure and easy to test in isolation.
    data = generate_ingredient_suggestions(user, favorites)
    return jsonify(data), 200