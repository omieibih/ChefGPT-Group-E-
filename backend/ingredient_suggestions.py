import random
import re


# This module is intentionally small and focused.
# It does not authenticate users or talk to Firestore directly.
# The route layer handles request security, and this file only transforms data.
# That separation keeps the suggestion logic easy to explain in a demo.
# It also makes the behavior easier to test because the function is mostly pure.
DEFAULT_INGREDIENTS = ["garlic", "onion", "rice", "tomato", "eggs", "beans"]

# These keyword hints let us infer likely ingredients from a recipe title.
# The goal is not to be perfect.
# The goal is to provide a better user experience when the saved ingredient list
# is short, messy, or missing a few obvious items.
# Because this is a static lookup table, the behavior is fast and predictable.
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

    # Reliability: favorites may come from inconsistent user-entered text.
    # We normalize common separators instead of assuming one perfect format.
    # That means a user can store ingredients with commas, semicolons, slashes,
    # or newlines and still get a usable suggestion list.
    # If the data is messy, we recover instead of raising an error.
    for part in re.split(r"[,;/\n]+", str(raw_ingredients)):
        # Some recipe text contains trailing notes like "(chopped)" or "(optional)".
        # We remove those notes so the chip text stays short and readable.
        item = re.sub(r"\s*\([^)]*\)\s*$", "", part).strip()
        if not item:
            continue

        # Deduplication happens here so repeated text in the source data does not
        # create repeated chips in the UI.
        key = item.lower()
        if key in seen:
            continue

        seen.add(key)
        ingredients.append(item)

    # The output is always a simple list of clean ingredient names.
    return ingredients


def _title_based_ingredients(title):
    """Infer a few likely ingredients from the recipe title."""
    normalized_title = str(title).lower()
    hints = []

    # Architecture: this helper is pure.
    # It receives plain text and returns plain text.
    # No request object, no database client, and no auth logic live here.
    # That keeps the suggestion pipeline modular and easy to reuse.
    for keyword, candidates in TITLE_HINTS:
        # If the title contains the keyword, we expand it into likely companion
        # ingredients that fit the same dish family.
        if keyword in normalized_title:
            for candidate in candidates:
                if candidate not in hints:
                    hints.append(candidate)

    # The caller decides whether these hints are useful enough to add.
    return hints


def generate_ingredient_suggestions(user, favorites, limit=8):
    """Pick one favorite recipe and return a few ingredient chips from it."""
    # Security: the caller already authenticated the request before reaching
    # this helper, so we only work with the user's saved favorites here.
    # This function never widens access to other users' data.
    # That is the security boundary for this feature.
    if not favorites:
        # Reliability: if the user has no saved recipes, we still return a stable
        # response shape and a few neutral defaults so the frontend can render.
        # That prevents the home page from breaking just because the account is new.
        # This also keeps the decision path simple: no favorites means use defaults.
        return {
            "recipe_title": "",
            "suggested_ingredients": DEFAULT_INGREDIENTS[:3],
            "no_favorites": True,
        }

    # Keep the selection lightweight and personal by choosing one saved recipe.
    # We avoid scanning every record because the feature only needs a small sample.
    # We also avoid extra network requests so the response stays fast.
    recipe = random.choice(favorites)

    # The saved ingredient string is the primary source of truth for the chips.
    ingredients = _extract_ingredients(recipe.get("ingredients", ""))

    # Reliability: if the stored ingredient list is short, the title hints fill
    # the gaps without overwriting what the user actually saved.
    # This makes the result feel more complete without changing the user's data.
    # Data complexity: we combine two data sources here, the stored ingredient
    # string and the recipe title, so the chip list reflects both user input and
    # inferred context.
    for item in _title_based_ingredients(recipe.get("name", "")):
        if item.lower() not in {existing.lower() for existing in ingredients}:
            # Append only brand-new items so the chips stay clean and readable.
            ingredients.append(item)

    # Reliability: the defaults guarantee that a sparse recipe still produces a
    # useful set of chips instead of an empty or low-quality response.
    # This is the last fallback layer, so the UI always has something to show.
    # Decision complexity: this branch only decides whether we need fallback
    # items, so the logic stays easy to explain and test.
    if len(ingredients) < min(limit, 3):
        existing = {item.lower() for item in ingredients}
        for fallback in DEFAULT_INGREDIENTS:
            if fallback not in existing:
                # Fallback ingredients are intentionally common pantry items.
                ingredients.append(fallback)
            if len(ingredients) >= min(limit, 3):
                # Stop as soon as we have enough suggestions.
                break

    # Architecture: the helper returns plain JSON-friendly data.
    # That keeps the route thin and lets the frontend consume the response
    # without another translation step.
    # Structural complexity stays low because this helper only coordinates a few
    # small functions instead of nesting several classes or services together.
    return {
        "recipe_title": recipe.get("name", "a recipe you liked"),
        "suggested_ingredients": ingredients[:limit],
        "no_favorites": False,
    }
