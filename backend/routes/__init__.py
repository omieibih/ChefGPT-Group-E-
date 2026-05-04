"""
backend/routes/__init__.py
Exposes every Blueprint so app.py can register them with a single import.

Usage in app.py
---------------
    from backend.routes import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)
"""

from backend.routes.Favorites_feature import favorites_bp
from backend.routes.Ingredient_Suggestion import ingredients_bp
from backend.routes.pages import pages_bp
from backend.routes.AI_Recipe_Generation import recipes_bp

all_blueprints = [pages_bp, recipes_bp, favorites_bp, ingredients_bp]