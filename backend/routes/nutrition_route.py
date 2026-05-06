from flask import Blueprint, request, jsonify
from backend.nutrition import get_nutrition

nutrition_bp = Blueprint("nutrition", __name__)

@nutrition_bp.route("/nutrition", methods=["GET"])
def nutrition():
    food = request.args.get("food")

    if not food:
        return jsonify({"error": "No food provided"}), 400

    result = get_nutrition(food)
    return jsonify(result)