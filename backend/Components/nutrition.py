import os

import requests
from flask import Blueprint, jsonify, request

APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")


def get_nutrition(food_query):
    if not APP_ID or not APP_KEY:
        return {"error": "API keys not set"}

    url = "https://api.edamam.com/api/nutrition-data"
    params = {"app_id": APP_ID, "app_key": APP_KEY, "ingr": food_query}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        return {
            "calories": data.get("calories"),
            "protein": data.get("totalNutrients", {}).get("PROCNT", {}).get("quantity"),
            "fat": data.get("totalNutrients", {}).get("FAT", {}).get("quantity"),
            "carbs": data.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity"),
        }
    except Exception as e:
        return {"error": str(e)}


nutrition_bp = Blueprint("nutrition", __name__)


@nutrition_bp.route("/nutrition", methods=["GET"])
def nutrition():
    food = request.args.get("food")
    if not food:
        return jsonify({"error": "No food provided"}), 400
    return jsonify(get_nutrition(food))