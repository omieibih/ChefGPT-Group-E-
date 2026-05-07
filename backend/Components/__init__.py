from backend.Components.favorites import favorites_bp
from backend.Components.recipes import recipes_bp
from backend.Components.shopping_list import shopping_bp
from backend.Components.nutrition import nutrition_bp
from backend.Components.experience_level import experience_level_bp
from backend.Components.ingredient_suggestions import ingredients_bp
from backend.Components.pages import pages_bp

all_blueprints = [
    pages_bp,
    recipes_bp,
    favorites_bp,
    ingredients_bp,
    experience_level_bp,
    nutrition_bp,
    shopping_bp,
]
