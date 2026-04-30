import random
import re


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
    """Split a stored ingredient string into clean, unique items."""
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
    """Infer a few likely ingredients from the recipe title."""
    normalized_title = str(title).lower()
    hints = []

    for keyword, candidates in TITLE_HINTS:
        if keyword in normalized_title:
            for candidate in candidates:
                if candidate not in hints:
                    hints.append(candidate)

    return hints


def generate_ingredient_suggestions(user, favorites, limit=8):
    """Pick one favorite recipe and return a few ingredient chips from it."""
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
