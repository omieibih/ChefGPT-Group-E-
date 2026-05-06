# =========================================================
# Shopping List Feature
# =========================================================

from flask import Blueprint, request, jsonify, render_template

# Import Firebase module (SAFE way — avoids ImportError issues)
import backend.firebase_init as firebase

# Import helper function that verifies Firebase login token
from backend.auth_helper import verify_firebase_token


# ---------------------------------------------------------
# Create Blueprint
# ---------------------------------------------------------
shopping_bp = Blueprint("shopping", __name__)


# =========================================================
# SHOPPING LIST PAGE
# =========================================================
@shopping_bp.route("/shopping-list")
def shopping_page():
    return render_template("shopping_list.html")


# =========================================================
# GET ALL SHOPPING LIST ITEMS
# =========================================================
@shopping_bp.route("/api/shopping-list", methods=["GET"])
def get_items():

    user = verify_firebase_token(request)

    docs = firebase.db.collection("users") \
        .document(user["uid"]) \
        .collection("shopping_list") \
        .stream()

    items = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        items.append(data)

    return jsonify(items)


# =========================================================
# ADD NEW SHOPPING LIST ITEM
# =========================================================
@shopping_bp.route("/api/shopping-list", methods=["POST"])
def add_item():

    user = verify_firebase_token(request)
    data = request.json

    item = {
        "name": data["name"],
        "completed": False
    }

    ref = firebase.db.collection("users") \
        .document(user["uid"]) \
        .collection("shopping_list") \
        .add(item)

    item["id"] = ref[1].id

    return jsonify(item)


# =========================================================
# DELETE SHOPPING LIST ITEM
# =========================================================
@shopping_bp.route("/api/shopping-list/<doc_id>", methods=["DELETE"])
def delete_item(doc_id):

    user = verify_firebase_token(request)

    firebase.db.collection("users") \
        .document(user["uid"]) \
        .collection("shopping_list") \
        .document(doc_id) \
        .delete()

    return jsonify({
        "success": True
    })