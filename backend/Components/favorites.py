"""
favorites.py — Favorites Feature
Overview:
    This file implements the Favorites feature for ChefGPT. It allows a logged-in
    user to save, view, and delete recipes they liked from the results page.

How it works:
    1. After recipes are generated on the results page, the user can click a
       "Save to Favorites" button next to any recipe.
    2. The frontend (templates/results.html) sends a POST request to /api/favorites
       with the recipe data (name, ingredients, instructions) and the user's Firebase
       auth token in the Authorization header.
    3. This file's API routes receive that request, verify the user's identity, and
       store the recipe in Firestore under the "favorites" collection.
    4. The user can visit /favorites (served by this file) to see all their saved
       recipes, which are fetched live from Firestore on page load.
    5. Each saved recipe has a "Remove" button that sends a DELETE request to
       /api/favorites/<doc_id>, which removes that document from Firestore.

Where data is stored:
    - All favorites are stored in Google Firestore under the "favorites" collection.
    - Each document in that collection contains:
        - uid:          The Firebase user ID of the owner (used to filter by user)
        - name:         The recipe name (string)
        - ingredients:  Comma-separated ingredient list (string)
        - instructions: Steps joined by " | " (string)
    - Firestore auto-generates a unique document ID for each saved recipe, which
      is used to identify it when deleting.

Files this feature interacts with:
    - templates/favorites.html      — The page that displays the user's saved recipes.
                                      Makes GET and DELETE calls to this file's API routes.
    - templates/results.html        — The results page where users click "Save to Favorites",
                                      triggering a POST to /api/favorites.
    - backend/Core/auth_helper.py   — Verifies the Firebase ID token sent with each request
                                      and returns the decoded user object.
    - backend/Core/firebase_init.py — Initializes the Firebase/Firestore connection.
                                      FIREBASE_AVAILABLE tells us if it's safe to use Firestore.
    - backend/Components/__init__.py — Imports favorites_bp and registers it with the Flask app.
    - static/firebase-config.js     — Frontend Firebase config used by favorites.html to get
                                      the user's auth token before calling the API.

Authentication:
    Every API route in this file requires the user to be logged in. Requests must
    include an "Authorization: Bearer <token>" header with a valid Firebase ID token.
    The _require_user() helper handles this check for all three routes.
"""

# Import the Firestore client from Firebase Admin SDK to interact with the database
from firebase_admin import firestore
# Import Flask utilities: Blueprint for grouping routes, jsonify for JSON responses,
# render_template to serve HTML pages, and request to read incoming HTTP data
from flask import Blueprint, jsonify, render_template, request

# Import helper that extracts and verifies the logged-in user from the request token
from backend.Core.auth_helper import get_current_user
# Import flags that tell us whether Firebase initialized successfully
from backend.Core.firebase_init import FIREBASE_AVAILABLE, FIREBASE_INIT_ERROR


# Database layer 

def save_favorite(user, data):
    # Connect to the Firestore database
    db = firestore.client()
    # Add a new document to the "favorites" collection with the user's info and recipe data
    db.collection("favorites").add({
        "uid": user["uid"],                    # Store the user's ID so we can filter by owner later
        "name": data.get("name"),              # Recipe name
        "ingredients": data.get("ingredients"),# List of ingredients for the recipe
        "instructions": data.get("instructions"), # Step-by-step cooking instructions
    })


def get_favorites(user):
    # Connect to the Firestore database
    db = firestore.client()
    # Query the "favorites" collection, returning only documents that belong to this user
    docs = db.collection("favorites").where("uid", "==", user["uid"]).stream()
    # Convert each Firestore document into a plain dict, adding the document ID as "id"
    return [{"id": d.id, **d.to_dict()} for d in docs]


def delete_favorite(user, doc_id):
    # Connect to the Firestore database
    db = firestore.client()
    # Get a reference to the specific document we want to delete
    doc_ref = db.collection("favorites").document(doc_id)
    # Fetch the document so we can check if it exists and who owns it
    doc = doc_ref.get()
    # If the document doesn't exist, nothing to delete — return False
    if not doc.exists:
        return False
    # Read the document's data as a dict (default to empty dict if None)
    data = doc.to_dict() or {}
    # Verify the document belongs to the requesting user — prevent deleting someone else's favorite
    if data.get("uid") != user["uid"]:
        return False
    # Delete the document from Firestore
    doc_ref.delete()
    # Return True to indicate the deletion was successful
    return True


# --- Blueprint ---

# Register this file's routes under the "favorites_api" blueprint name
favorites_bp = Blueprint("favorites_api", __name__)


def _require_user():
    # If Firebase failed to initialize, return a 503 Service Unavailable error
    if not FIREBASE_AVAILABLE:
        return None, (
            jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}),
            503,
        )
    # Try to extract the authenticated user from the request's Authorization header
    user = get_current_user(request)
    # If no valid user was found, return a 401 Unauthorized error
    if not user:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    # Return the user object and no error
    return user, None


# Serve the favorites HTML page when the user navigates to /favorites
@favorites_bp.route("/favorites")
def favorites_page():
    return render_template("favorites.html")


# Handle POST requests to save a new favorite recipe for the logged-in user
@favorites_bp.route("/api/favorites", methods=["POST"])
def api_save_favorite():
    # Authenticate the user; return an error response if authentication fails
    user, err = _require_user()
    if err:
        return err
    # Save the recipe data from the request body to Firestore
    save_favorite(user, request.get_json())
    # Respond with a success message and HTTP 200 OK
    return jsonify({"message": "Saved!"}), 200


# Handle GET requests to retrieve all favorites for the logged-in user
@favorites_bp.route("/api/favorites", methods=["GET"])
def api_get_favorites():
    # Authenticate the user; return an error response if authentication fails
    user, err = _require_user()
    if err:
        return err
    # Fetch and return the user's favorites as a JSON array
    return jsonify(get_favorites(user)), 200


# Handle DELETE requests to remove a specific favorite by its Firestore document ID
@favorites_bp.route("/api/favorites/<doc_id>", methods=["DELETE"])
def api_delete_favorite(doc_id):
    # Authenticate the user; return an error response if authentication fails
    user, err = _require_user()
    if err:
        return err
    # Delete the favorite document (ownership is verified inside delete_favorite)
    delete_favorite(user, doc_id)
    # Respond with a success message and HTTP 200 OK
    return jsonify({"message": "Deleted"}), 200
