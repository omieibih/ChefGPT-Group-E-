from firebase_admin import firestore
from flask import Blueprint, jsonify, render_template, request

from backend.Core.auth_helper import get_current_user
from backend.Core.firebase_init import FIREBASE_AVAILABLE, FIREBASE_INIT_ERROR


# --- DB layer ---

def save_favorite(user, data):
    db = firestore.client()
    db.collection("favorites").add({
        "uid": user["uid"],
        "name": data.get("name"),
        "ingredients": data.get("ingredients"),
        "instructions": data.get("instructions"),
    })


def get_favorites(user):
    db = firestore.client()
    docs = db.collection("favorites").where("uid", "==", user["uid"]).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]


def delete_favorite(user, doc_id):
    db = firestore.client()
    doc_ref = db.collection("favorites").document(doc_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False
    data = doc.to_dict() or {}
    if data.get("uid") != user["uid"]:
        return False
    doc_ref.delete()
    return True


# --- Blueprint ---

favorites_bp = Blueprint("favorites_api", __name__)


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


@favorites_bp.route("/favorites")
def favorites_page():
    return render_template("favorites.html")


@favorites_bp.route("/api/favorites", methods=["POST"])
def api_save_favorite():
    user, err = _require_user()
    if err:
        return err
    save_favorite(user, request.get_json())
    return jsonify({"message": "Saved!"}), 200


@favorites_bp.route("/api/favorites", methods=["GET"])
def api_get_favorites():
    user, err = _require_user()
    if err:
        return err
    return jsonify(get_favorites(user)), 200


@favorites_bp.route("/api/favorites/<doc_id>", methods=["DELETE"])
def api_delete_favorite(doc_id):
    user, err = _require_user()
    if err:
        return err
    delete_favorite(user, doc_id)
    return jsonify({"message": "Deleted"}), 200