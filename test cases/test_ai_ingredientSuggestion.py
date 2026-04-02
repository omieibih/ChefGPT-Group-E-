# Reviewer runs it with:
# pytest -v test_ai_ingredientSuggestion.py


# test_ai_ingredient.py
from app import get_ingredients

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