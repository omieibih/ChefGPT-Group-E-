#beginning of favorite feature in backend
# SaveRecipeToFavorites.py

favorites = []

def save_recipe(recipe_name):
    if recipe_name == "":
        return "Please enter a recipe name."
    if recipe_name in favorites:
        return True  # Already saved, skip duplicate
    favorites.append(recipe_name)
    return True

def get_favorites():
    return favorites

def remove_recipe(recipe_name):
    if recipe_name in favorites:
        favorites.remove(recipe_name)
