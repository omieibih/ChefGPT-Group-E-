def get_recipes(ingredients, budget, experience_level="beginner"):
    return [
        {
            "name": "Simple Stir Fry",
            "description": f"A {experience_level}-friendly meal using {ingredients}.",
            "core_ingredients": [item.strip() for item in ingredients.split(",")],
            "additional_ingredients": ["soy sauce", "oil", "garlic"],
            "instructions": [
                "Prep your ingredients.",
                "Heat oil in a pan.",
                "Cook everything together until done.",
                "Season and serve."
            ]
        },
        {
            "name": "Rice Bowl",
            "description": "A quick bowl meal using what you already have.",
            "core_ingredients": [item.strip() for item in ingredients.split(",")],
            "additional_ingredients": ["rice", "salt", "pepper"],
            "instructions": [
                "Cook the rice.",
                "Prepare the main ingredients.",
                "Assemble everything in a bowl.",
                "Serve warm."
            ]
        },
        {
            "name": "Skillet Meal",
            "description": "A one-pan budget-friendly recipe.",
            "core_ingredients": [item.strip() for item in ingredients.split(",")],
            "additional_ingredients": ["butter", "onion"],
            "instructions": [
                "Heat a skillet.",
                "Add onion and cook briefly.",
                "Add your ingredients and cook through.",
                "Serve hot."
            ]
        }
    ]