from firebase_admin import firestore
from flask import Blueprint, jsonify, render_template, request

from backend.Core.auth_helper import get_current_user

shopping_bp = Blueprint("shopping", __name__)


@shopping_bp.route("/shopping-list")
def shopping_page():
    return render_template("shopping_list.html")


@shopping_bp.route("/api/shopping-list", methods=["GET"])
def get_items():
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    docs = (
        firestore.client()
        .collection("users")
        .document(user["uid"])
        .collection("shopping_list")
        .stream()
    )

    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)

    return jsonify(items)


@shopping_bp.route("/api/shopping-list", methods=["POST"])
def add_item():
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    item = {"name": data["name"], "completed": False}

    ref = (
        firestore.client()
        .collection("users")
        .document(user["uid"])
        .collection("shopping_list")
        .add(item)
    )

    item["id"] = ref[1].id
    return jsonify(item)


@shopping_bp.route("/api/shopping-list/<doc_id>", methods=["DELETE"])
def delete_item(doc_id):
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    (
        firestore.client()
        .collection("users")
        .document(user["uid"])
        .collection("shopping_list")
        .document(doc_id)
        .delete()
    )

    return jsonify({"success": True})