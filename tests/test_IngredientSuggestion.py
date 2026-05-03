# Reviewer runs it with:
# pytest -v tests/test_IngredientSuggestion.py

import sys
import os

# Add the parent folder of app.py to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))



# test_ai_ingredient.py
from app import get_ingredients
from backend.ingredient_suggestions import generate_ingredient_suggestions

# Test 1: High protein query
def test_high_protein():
    result = get_ingredients("high protein")
    assert "chicken" in result
    assert "eggs" in result

# Test 2: Cheap meal query
def test_cheap_meal():
    result = get_ingredients("cheap meal")
    assert "rice" in result
    assert "pasta" in result

# Test 3: Vegan query
def test_vegan():
    result = get_ingredients("vegan")
    assert "tofu" in result
    assert "lentils" in result

# Test 4: Empty input (edge case)
def test_empty_input():
    result = get_ingredients("")
    assert result == ["Please enter a request."]

# Test 5: Unknown input (fallback behavior)
def test_unknown_input():
    result = get_ingredients("random words")
    assert "tomatoes" in result
    assert "onions" in result

# Test 6: Case insensitivity
def test_case_insensitive():
    result = get_ingredients("HIGH PROTEIN")
    assert "chicken" in result


def test_generate_ingredient_suggestions_parses_and_limits_items():
    favorites = [
        {"name": "Pasta Night", "ingredients": "garlic, onion; basil / parmesan, garlic, tomato"}
    ]

    result = generate_ingredient_suggestions({"uid": "user-1"}, favorites, limit=3)

    assert result["recipe_title"] == "Pasta Night"
    assert result["suggested_ingredients"] == ["garlic", "onion", "basil"]


def test_generate_ingredient_suggestions_uses_recipe_title_hints():
    favorites = [
        {"name": "Chicken Parmesan", "ingredients": "chicken"}
    ]

    result = generate_ingredient_suggestions({"uid": "user-1"}, favorites, limit=5)

    assert result["recipe_title"] == "Chicken Parmesan"
    assert "chicken" in result["suggested_ingredients"]
    assert "pasta" in result["suggested_ingredients"]
    assert "tomato" in result["suggested_ingredients"]
    assert "cheese" in result["suggested_ingredients"]


def test_generate_ingredient_suggestions_uses_fallback_when_empty():
    result = generate_ingredient_suggestions({"uid": "user-1"}, [], limit=3)

    assert result["no_favorites"] is True
    assert result["suggested_ingredients"] == ["garlic", "onion", "rice"]