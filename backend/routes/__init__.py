"""
backend/routes/__init__.py
Exposes every Blueprint so app.py can register them with a single import.

Usage in app.py
---------------
    from backend.routes import all_blueprints
    for bp in all_blueprints:
        app.register_blueprint(bp)
"""

from backend.routes.favorites import favorites_bp
from backend.routes.ingredients import ingredients_bp
from backend.routes.pages import pages_bp
from backend.routes.recipes import recipes_bp

all_blueprints = [pages_bp, recipes_bp, favorites_bp, ingredients_bp]