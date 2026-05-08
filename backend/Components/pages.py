"""
pages.py — Page Routing

Overview:
    This file handles the basic HTML page routes for ChefGPT. It does not contain
    any business logic — its only job is to serve the correct HTML template when
    a user navigates to a URL in their browser.

How it works:
    - The home page (/) lets the user pick their cooking experience level.
    - Submitting that form POSTs to /ingredients, which carries the chosen level
      forward into the next page as a template variable.
    - /login serves the login page for unauthenticated users.
    - All actual feature logic (recipe generation, favorites, shopping list, etc.)
      lives in other files in this Components folder.

Files this feature interacts with:
    - templates/index.html       — Home page; contains the experience level dropdown
                                   form that POSTs to /ingredients.
    - templates/ingredients.html — Ingredients input page; receives experience_level
                                   as a template variable and passes it as a hidden
                                   field when the form submits to /results.
    - templates/login.html       — Login page served to unauthenticated users.
    - backend/Components/__init__.py — Imports pages_bp and registers it with the Flask app.

Authentication:
    These routes do not require authentication. The frontend JavaScript on index.html
    and ingredients.html handles auth state and redirects to /login if the user is
    not logged in.
"""

# Import Blueprint to define a group of related routes,
# render_template to load and return HTML files from the templates/ folder,
# and request to read data submitted via HTML forms
from flask import Blueprint, render_template, request

# Create the Blueprint object — Flask uses this to register all routes
# defined below when app.py calls app.register_blueprint()
pages_bp = Blueprint("pages", __name__)


# Route: GET /
# Serves the home page where the user selects their cooking experience level
@pages_bp.route("/")
def home():
    # Render and return templates/index.html with no extra data needed
    return render_template("index.html")


# Route: POST /ingredients
# Called when the user submits the experience level form on the home page.
# Reads the selected level and passes it into the next template so it
# can be displayed and carried forward as a hidden field on the ingredients form.
@pages_bp.route("/ingredients", methods=["POST"])
def ingredients():
    # Read the "experience_level" field from the submitted form data
    # (e.g. "Beginner", "Intermediate", or "Advanced")
    experience_level = request.form.get("experience_level")

    # Render templates/ingredients.html and inject the experience level
    # so the template can display it and embed it in the next form as a hidden field
    return render_template("ingredients.html", experience_level=experience_level)


# Route: GET /login
# Serves the login page for users who are not yet authenticated
@pages_bp.route("/login")
def login():
    # Render and return templates/login.html — Firebase handles the actual auth on the frontend
    return render_template("login.html")
