from firebase_admin import firestore
from flask import Blueprint, jsonify, request

from backend.Core.auth_helper import get_current_user
from backend.Core.firebase_init import FIREBASE_AVAILABLE, FIREBASE_INIT_ERROR


# --- DB layer ---

def save_experience_level(user, experience_level):
    db = firestore.client()
    db.collection("users").document(user["uid"]).set(
        {
            "uid": user["uid"],
            "email": user.get("email"),
            "experience_level": experience_level,
        },
        merge=True,
    )


def get_experience_level(user):
    db = firestore.client()
    doc = db.collection("users").document(user["uid"]).get()
    if not doc.exists:
        return "Beginner"
    data = doc.to_dict() or {}
    return data.get("experience_level", "Beginner")


# --- Blueprint ---

experience_level_bp = Blueprint("experience_level_api", __name__)


def _require_user():
    if not FIREBASE_AVAILABLE:
        return None, (
            jsonify({"error": "Firebase is not configured.", "details": FIREBASE_INIT_ERROR}),
            503,
        )
    user = get_current_user(request)
    if not user:
        return None, (jsonify({"error": "Unauthorized"}), 401)
    return user, None


@experience_level_bp.route("/api/experience-level", methods=["POST"])
def api_save_experience_level():
    user, err = _require_user()
    if err:
        return err
    data = request.get_json() or {}
    experience_level = data.get("experience_level", "Beginner")
    if experience_level not in ["Beginner", "Intermediate", "Advanced"]:
        return jsonify({"error": "Invalid experience level"}), 400
    save_experience_level(user, experience_level)
    return jsonify({"message": "Experience level saved!"}), 200


@experience_level_bp.route("/api/experience-level", methods=["GET"])
def api_get_experience_level():
    user, err = _require_user()
    if err:
        return err
    return jsonify({"experience_level": get_experience_level(user)}), 200