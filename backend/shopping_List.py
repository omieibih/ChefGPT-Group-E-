#beginning of shopping_list feature
# Import Flask tools needed for routes and JSON responses
from flask import Blueprint, request, jsonify, render_template


from firebase_admin import firestore
from backend.auth_helper import get_current_user




# ---------------------------------------------------------
# Create a Blueprint
# ---------------------------------------------------------
# Blueprints help organize routes into separate files
# instead of putting everything inside app.py
# ---------------------------------------------------------
shopping_bp = Blueprint("shopping", __name__)




# =========================================================
# SHOPPING LIST PAGE
# =========================================================
# This route loads the shopping list HTML page
#
# URL:
#   /shopping-list
#
# Method:
#   GET
#
# Example:
#   User clicks "Shopping List" in navigation bar
# =========================================================
@shopping_bp.route("/shopping-list")
def shopping_page():


   # Render the shopping_list.html template
   return render_template("shopping_list.html")




# =========================================================
# GET ALL SHOPPING LIST ITEMS
# =========================================================
# This route gets all shopping list items for the user
#
# URL:
#   /api/shopping-list
#
# Method:
#   GET
#
# Returns:
#   JSON list of shopping list items
# =========================================================
@shopping_bp.route("/api/shopping-list", methods=["GET"])
def get_items():


   # ---------------------------------------------
   # Verify Firebase token
   # ---------------------------------------------
   # This checks if the user is logged in
   #
   # If token is invalid:
   #   request will fail
   #
   # If valid:
   #   returns user info including uid
   # ---------------------------------------------
   user = get_current_user(request)


   # ---------------------------------------------
   # Access Firestore
   # ---------------------------------------------
   #
   # Firestore structure:
   #
   # users
   #   -> user_uid
   #       -> shopping_list
   #           -> item documents
   #
   # .stream() gets ALL documents
   # ---------------------------------------------
   docs = firestore.client().collection("users") \
       .document(user["uid"]) \
       .collection("shopping_list") \
       .stream()


   # Empty Python list to store shopping items
   items = []


   # ---------------------------------------------
   # Loop through all Firestore documents
   # ---------------------------------------------
   for doc in docs:


       # Convert Firestore document into dictionary
       data = doc.to_dict()


       # Add document ID
       # Needed for deleting items later
       data["id"] = doc.id


       # Add item to list
       items.append(data)


   # Return all items as JSON
   return jsonify(items)




# =========================================================
# ADD NEW SHOPPING LIST ITEM
# =========================================================
# This route creates a new shopping list item
#
# URL:
#   /api/shopping-list
#
# Method:
#   POST
#
# Expected JSON:
# {
#   "name": "milk"
# }
# =========================================================
@shopping_bp.route("/api/shopping-list", methods=["POST"])
def add_item():


   # Verify logged-in user
   user = get_current_user(request)


   # Get JSON data from frontend request
   data = request.json


   # ---------------------------------------------
   # Create shopping list item object
   # ---------------------------------------------
   item = {


       # Ingredient name
       "name": data["name"],


       # Track whether user completed/bought item
       "completed": False
   }


   # ---------------------------------------------
   # Save item to Firestore
   # ---------------------------------------------
   #
   # Firestore automatically creates document ID
   #
   # Example:
   # users/abc123/shopping_list/randomDocId
   # ---------------------------------------------
   ref = firestore.client().collection("users") \
       .document(user["uid"]) \
       .collection("shopping_list") \
       .add(item)


   # Save generated Firestore document ID
   item["id"] = ref[1].id


   # Return created item as JSON
   return jsonify(item)




# =========================================================
# DELETE SHOPPING LIST ITEM
# =========================================================
# This route deletes an item from Firestore
#
# URL:
#   /api/shopping-list/<doc_id>
#
# Method:
#   DELETE
#
# Example:
#   DELETE /api/shopping-list/abc123
# =========================================================
@shopping_bp.route("/api/shopping-list/<doc_id>", methods=["DELETE"])
def delete_item(doc_id):


   # Verify user is logged in
   user = get_current_user(request)


   # ---------------------------------------------
   # Delete Firestore document
   # ---------------------------------------------
   firestore.client().collection("users") \
       .document(user["uid"]) \
       .collection("shopping_list") \
       .document(doc_id) \
       .delete()


   # Return success response
   return jsonify({
       "success": True
   })


