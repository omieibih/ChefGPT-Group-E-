# Reviewer runs it with:
# PYTHONPATH=. pytest -v tests/test_nutrition.py
from app import get_nutrition

# Test 1: Valid food returns a dictionary with expected keys
def test_valid_food_returns_nutrition():
    result = get_nutrition("apple")

    assert isinstance(result, dict)
    assert "calories" in result
    assert "protein" in result
    assert "carbs" in result
    assert "fat" in result


# Test 2: Nutrition values should be non-negative
def test_nutrition_values_positive():
    result = get_nutrition("banana")

    assert result["calories"] >= 0
    assert result["protein"] >= 0
    assert result["carbs"] >= 0
    assert result["fat"] >= 0


# Test 3: Empty input should return an error message
def test_empty_input():
    result = get_nutrition("")

    assert result == "Please enter a food name."


# Test 4: Invalid food should return a message
def test_invalid_food():
    result = get_nutrition("asdfghjkl")

    assert result == "Food not found."


# Test 5: Case insensitivity
def test_case_insensitive():
    result1 = get_nutrition("Apple")
    result2 = get_nutrition("apple")

    assert result1 == result2


# Test 6: Output structure consistency
def test_output_structure():
    result = get_nutrition("apple")

    # Ensure all required keys exist
    expected_keys = {"calories", "protein", "carbs", "fat"}
    assert expected_keys.issubset(result.keys())