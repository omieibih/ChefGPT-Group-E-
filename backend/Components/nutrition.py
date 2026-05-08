# =============================================================================
# nutrition.py
#
# Fetches nutritional data for a given food query using the Edamam Nutrition
# Analysis API. Exposes a single Flask GET endpoint (/nutrition?food=<query>)
# that returns calories, protein, fat, and carbohydrates for the requested food.
# =============================================================================

import os          # Used to read API credentials from environment variables

import requests                                   # HTTP client for calling the Edamam API
from flask import Blueprint, jsonify, request     # Flask utilities for routing and JSON responses

# Read the Edamam API credentials from environment variables set in .env
APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")


def get_nutrition(food_query):
    # Refuse to make the API call if credentials are missing — avoids a confusing 401 from Edamam
    if not APP_ID or not APP_KEY:
        return {"error": "API keys not set"}

    # Base URL for the Edamam Nutrition Analysis API
    url = "https://api.edamam.com/api/nutrition-data"
    # Build the query parameters: credentials plus the free-text ingredient string
    params = {"app_id": APP_ID, "app_key": APP_KEY, "ingr": food_query}

    try:
        response = requests.get(url, params=params)  # Send the GET request to Edamam
        data = response.json()                        # Parse the JSON response body into a dict
        return {
            # Top-level "calories" field is a plain integer in the Edamam response
            "calories": data.get("calories"),
            # Protein is nested under totalNutrients -> PROCNT -> quantity
            "protein": data.get("totalNutrients", {}).get("PROCNT", {}).get("quantity"),
            # Fat is nested under totalNutrients -> FAT -> quantity
            "fat": data.get("totalNutrients", {}).get("FAT", {}).get("quantity"),
            # Carbohydrates are nested under totalNutrients -> CHOCDF -> quantity
            "carbs": data.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity"),
        }
    except Exception as e:
        # Catch network errors, JSON decode failures, etc. and surface a readable message
        return {"error": str(e)}


# Register a Flask Blueprint to group the nutrition route under its own namespace
nutrition_bp = Blueprint("nutrition", __name__)


@nutrition_bp.route("/nutrition", methods=["GET"])
def nutrition():
    food = request.args.get("food")   # Read the "food" query parameter from the URL
    if not food:
        return jsonify({"error": "No food provided"}), 400  # Require a food name; 400 Bad Request if absent
    return jsonify(get_nutrition(food))  # Fetch nutrition data and return it as JSON
