import random


def generate_ingredient_suggestions(user, favorites, limit=8):
    """Pick one favorite recipe and return a few ingredient chips from it."""
    if not favorites:
        return {
            "recipe_title": "",
            "suggested_ingredients": ["garlic", "onion", "rice"],
            "no_favorites": True,
        }

    recipe = random.choice(favorites)
    raw_ingredients = str(recipe.get("ingredients", ""))
    ingredients = []

    for part in raw_ingredients.split(","):
        item = part.strip()
        if item and item not in ingredients:
            ingredients.append(item)
        if len(ingredients) >= 3:
            break

    return {
        "recipe_title": recipe.get("name", "a recipe you liked"),
        "suggested_ingredients": ingredients,
        "no_favorites": False,
    }
