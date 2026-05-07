import os
import requests

APP_ID = os.getenv("EDAMAM_APP_ID")
APP_KEY = os.getenv("EDAMAM_APP_KEY")

def get_nutrition(food_query):
    if not APP_ID or not APP_KEY:
        return {"error": "API keys not set"}

    url = "https://api.edamam.com/api/nutrition-data"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "ingr": food_query
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        return {
            "calories": data.get("calories"),
            "protein": data.get("totalNutrients", {}).get("PROCNT", {}).get("quantity"),
            "fat": data.get("totalNutrients", {}).get("FAT", {}).get("quantity"),
            "carbs": data.get("totalNutrients", {}).get("CHOCDF", {}).get("quantity")
        }

    except Exception as e:
        return {"error": str(e)}