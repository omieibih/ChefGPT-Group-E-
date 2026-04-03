# Reviewer runs it with:
# pytest -v tests/test_SaveRecipeToFavorites.py

import sys
import os
import pytest

# Add the parent folder of app.py to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import save_recipe, get_favorites, remove_recipe, _favorites

# Clear favorites before each test to prevent leftover data from affecting results
@pytest.fixture(autouse=True)
def clear_favorites():
    _favorites.clear()
    yield

# Test 1: Save a valid recipe
def test_save_valid_recipe():
    result = save_recipe("Spaghetti Carbonara")
    assert result == True

# Test 2: Saved recipe appears in favorites list
def test_saved_recipe_appears_in_favorites():
    save_recipe("Chicken Adobo")
    favorites = get_favorites()
    assert "Chicken Adobo" in favorites

# Test 3: Save multiple recipes
def test_save_multiple_recipes():
    save_recipe("Caesar Salad")
    save_recipe("Beef Stew")
    favorites = get_favorites()
    assert "Caesar Salad" in favorites
    assert "Beef Stew" in favorites

# Test 4: Empty input (edge case)
def test_empty_recipe_name():
    result = save_recipe("")
    assert result == "Please enter a recipe name."

# Test 5: Duplicate recipe (should not save twice)
def test_duplicate_recipe():
    save_recipe("Pancakes")
    save_recipe("Pancakes")
    favorites = get_favorites()
    assert favorites.count("Pancakes") == 1

# Test 6: Remove a recipe from favorites
def test_remove_recipe_from_favorites():
    save_recipe("Greek Salad")
    remove_recipe("Greek Salad")
    favorites = get_favorites()
    assert "Greek Salad" not in favorites