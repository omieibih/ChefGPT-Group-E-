# =============================================================================
# experience_level.py
#
# Manages a user's cooking experience level (Beginner, Intermediate, Advanced).
# Provides a Firestore DB layer for reading/writing the level, and two Flask
# API endpoints so the frontend can get and update it per authenticated user.
# =============================================================================

from firebase_admin import firestore                    # Firestore client from the Firebase Admin SDK
from flask import Blueprint, jsonify, request           # Flask utilities for routing and responses

from backend.Core.auth_helper import get_current_user  # Extracts and verifies the user from the request token
from backend.Core.firebase_init import FIREBASE_AVAILABLE, FIREBASE_INIT_ERROR  # Firebase health flags


# --- DB layer ---

def save_experience_level(user, experience_level):
    # Get a Firestore client instance
    db = firestore.client()
    # Write (or merge) the user's experience level into their Firestore document
    db.collection("users").document(user["uid"]).set(
        {
            "uid": user["uid"],                  # Store the user's unique ID
            "email": user.get("email"),          # Store their email (may be None if not present)
            "experience_level": experience_level, # The level string: Beginner, Intermediate, or Advanced
        },
        merge=True,  # Merge so existing fields (e.g. shopping list) are not overwritten
    )


def get_experience_level(user):
    # Get a Firestore client instance
    db = firestore.client()
    # Fetch the user's document from the "users" collection
    doc = db.collection("users").document(user["uid"]).get()
    if not doc.exists:
        return "Beginner"  # Default to Beginner if the user has no document yet
    data = doc.to_dict() or {}  # Convert the document snapshot to a plain dict; fall back to {} if None
    return data.get("experience_level", "Beginner")  # Return the stored level, defaulting to Beginner


# --- Blueprint ---

# Register a Flask Blueprint so these routes are grouped under the "experience_level_api" namespace
experience_level_bp = Blueprint("experience_level_api", __name__)


def _require_user():
    # Reject the request early if Firebase is not initialised (e.g. missing env vars)
    if not FIREBASE_AVAILABLE:
        return None, (
            jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}),
            503,  # 503 Service Unavailable — the dependency is down, not the caller's fault
        )
    # Verify the Bearer token from the Authorization header and decode the user
    user = get_current_user(request)
    if not user:
        return None, (jsonify({"error": "Unauthorized"}), 401)  # Token missing, expired, or invalid
    return user, None  # Return the verified user and no error


@experience_level_bp.route("/api/experience-level", methods=["POST"])
def api_save_experience_level():
    # Authenticate the caller; bail out with the error response if auth fails
    user, err = _require_user()
    if err:
        return err
    data = request.get_json() or {}  # Parse the JSON body; fall back to empty dict if body is absent
    experience_level = data.get("experience_level", "Beginner")  # Read the submitted level, default Beginner
    # Reject values that are not one of the three allowed levels
    if experience_level not in ["Beginner", "Intermediate", "Advanced"]:
        return jsonify({"error": "Invalid experience level"}), 400
    save_experience_level(user, experience_level)  # Persist the validated level to Firestore
    return jsonify({"message": "Experience level saved!"}), 200  # Confirm success to the client


@experience_level_bp.route("/api/experience-level", methods=["GET"])
def api_get_experience_level():
    # Authenticate the caller; bail out with the error response if auth fails
    user, err = _require_user()
    if err:
        return err
    # Fetch and return the user's current experience level from Firestore
    return jsonify({"experience_level": get_experience_level(user)}), 200
