from firebase_admin import firestore
from flask import Blueprint, jsonify, render_template, request

# Helper function to get the currently logged-in user
from backend.Core.auth_helper import get_current_user

# Create blueprint for shopping list routes
shopping_bp = Blueprint("shopping", __name__)


# Route to render the shopping list page
@shopping_bp.route("/shopping-list")
def shopping_page():
    return render_template("shopping_list.html")


# Route to get all shopping list items for the current user
@shopping_bp.route("/api/shopping-list", methods=["GET"])
def get_items():
    # Check if user is authenticated
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Get shopping list documents from Firestore
    docs = (
        firestore.client()
        .collection("users")
        .document(user["uid"])
        .collection("shopping_list")
        .stream()
    )

    # Store all items in a list
    items = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id  # Add document ID to item data
        items.append(data)

    return jsonify(items)


# Route to add a new shopping list item
@shopping_bp.route("/api/shopping-list", methods=["POST"])
def add_item():
    # Check if user is authenticated
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Get JSON data from request
    data = request.json

    # Create new shopping item
    item = {"name": data["name"], "completed": False}

    # Add item to Firestore
    ref = (
        firestore.client()
        .collection("users")
        .document(user["uid"])
        .collection("shopping_list")
        .add(item)
    )

    # Save generated document ID into item data
    item["id"] = ref[1].id

    return jsonify(item)


# Route to delete a shopping list item by document ID
@shopping_bp.route("/api/shopping-list/<doc_id>", methods=["DELETE"])
def delete_item(doc_id):
    # Check if user is authenticated
    user = get_current_user(request)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    # Delete item from Firestore
    (
        firestore.client()
        .collection("users")
        .document(user["uid"])
        .collection("shopping_list")
        .document(doc_id)
        .delete()
    )

    return jsonify({"success": True})