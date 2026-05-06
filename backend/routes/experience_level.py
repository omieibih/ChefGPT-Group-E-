"""
backend/routes/experience_level.py
REST API for saving and retrieving a user's cooking experience level.
"""

from flask import Blueprint, jsonify, request

from backend.auth_helper import get_current_user
from backend.experience_level import get_experience_level, save_experience_level
from backend.firebase_init import FIREBASE_AVAILABLE, FIREBASE_INIT_ERROR

experience_level_bp = Blueprint(
    "experience_level_api",
    __name__,
    url_prefix="/api/experience-level",
)


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


@experience_level_bp.route("", methods=["POST"])
def api_save_experience_level():
    """Save the authenticated user's cooking experience level."""
    user, err = _require_user()
    if err:
        return err

    data = request.get_json() or {}
    experience_level = data.get("experience_level", "Beginner")

    if experience_level not in ["Beginner", "Intermediate", "Advanced"]:
        return jsonify({"error": "Invalid experience level"}), 400

    save_experience_level(user, experience_level)
    return jsonify({"message": "Experience level saved!"}), 200


@experience_level_bp.route("", methods=["GET"])
def api_get_experience_level():
    """Return the authenticated user's saved cooking experience level."""
    user, err = _require_user()
    if err:
        return err

    return jsonify({"experience_level": get_experience_level(user)}), 200