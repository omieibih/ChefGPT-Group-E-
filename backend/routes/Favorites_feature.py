"""
backend/routes/favorites.py
REST API for saving, listing, and deleting a user's favourite recipes.

All endpoints require a valid Firebase ID token in the Authorization header.
Delegates database operations to backend.favorites (Firestore layer).
"""

from flask import Blueprint, jsonify, request

from backend.auth_helper import get_current_user
from backend.favorites import delete_favorite, get_favorites, save_favorite
from backend.firebase_init import FIREBASE_AVAILABLE, FIREBASE_INIT_ERROR

favorites_bp = Blueprint("favorites_api", __name__, url_prefix="/api/favorites")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _require_user():
    """
    Validates the Firebase token and returns (user, None) on success or
    (None, error_response) when authentication fails.
    """
    if not FIREBASE_AVAILABLE:
        return None, (
            jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}),
            503,
        )

    user = get_current_user(request)
    if not user:
        return None, (jsonify({"error": "Unauthorized"}), 401)

    return user, None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@favorites_bp.route("", methods=["POST"])
def api_save_favorite():
    """Save a new favourite recipe for the authenticated user."""
    user, err = _require_user()
    if err:
        return err

    save_favorite(user, request.get_json())
    return jsonify({"message": "Saved!"}), 200


@favorites_bp.route("", methods=["GET"])
def api_get_favorites():
    """Return all favourite recipes owned by the authenticated user."""
    user, err = _require_user()
    if err:
        return err

    return jsonify(get_favorites(user)), 200


@favorites_bp.route("/<doc_id>", methods=["DELETE"])
def api_delete_favorite(doc_id):
    """Delete one favourite recipe by its Firestore document ID."""
    user, err = _require_user()
    if err:
        return err

    delete_favorite(user, doc_id)
    return jsonify({"message": "Deleted"}), 200