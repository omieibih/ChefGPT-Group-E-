import pytest
from unittest.mock import patch


# This fixture creates a test version of the Flask app.
# The test client lets us send fake requests to the app
# without having to manually run the website in a browser.
@pytest.fixture
def client():
    from app import app

    # TESTING mode gives clearer errors during test failures.
    app.config["TESTING"] = True

    # Create a temporary Flask test client for each test.
    with app.test_client() as client:
        yield client


def test_ingredients_page_receives_experience_level(client):
    """
    Test that the experience level selected on the first page
    is passed correctly to the ingredients page.
    """

    # Simulate the user choosing "Intermediate" and submitting
    # the form to the /ingredients route.
    response = client.post(
        "/ingredients",
        data={
            "experience_level": "Intermediate"
        }
    )

    # Make sure the ingredients page loads successfully.
    assert response.status_code == 200

    # Make sure the selected experience level appears somewhere
    # in the HTML response.
    assert b"Intermediate" in response.data


@patch("backend.Components.recipes.get_recipes")
def test_results_uses_selected_experience_level(mock_get_recipes, client):
    """
    Test that the /results route passes the selected experience level
    into the recipe generation function.
    """

    # Mock get_recipes so the test does not call the real AI API.
    # This makes the test faster and avoids needing an API key.
    mock_get_recipes.return_value = [
        {
            "name": "Test Recipe",
            "description": "A test recipe.",
            "core_ingredients": ["eggs"],
            "additional_ingredients": ["salt"],
            "instructions": ["Cook the eggs."]
        }
    ]

    # Simulate the user submitting ingredients, budget,
    # experience level, and dietary filter to the results page.
    response = client.post(
        "/results",
        data={
            "ingredients": "eggs",
            "budget": "10",
            "experience_level": "Advanced",
            "dietary_filter": ""
        }
    )

    # Make sure the results page loads successfully.
    assert response.status_code == 200

    # Make sure /results called get_recipes with the exact values
    # from the form, including the selected experience level.
    mock_get_recipes.assert_called_once_with(
        "eggs",
        "10",
        "Advanced",
        ""
    )

    # Make sure the returned page is actually the results page.
    assert b"Results" in response.data or b"ChefGPT" in response.data


@patch("backend.Components.recipes.get_recipes")
def test_results_defaults_to_beginner_when_experience_level_missing(mock_get_recipes, client):
    """
    Test the reliability fallback: if no experience level is submitted,
    the backend should default to Beginner instead of crashing.
    """

    # Mock get_recipes so this test does not call the real AI API.
    mock_get_recipes.return_value = [
        {
            "name": "Beginner Test Recipe",
            "description": "A beginner-friendly test recipe.",
            "core_ingredients": ["pasta"],
            "additional_ingredients": ["sauce"],
            "instructions": ["Boil pasta.", "Add sauce."]
        }
    ]

    # Simulate a form submission where the user gives ingredients
    # and budget but no experience_level value.
    response = client.post(
        "/results",
        data={
            "ingredients": "pasta",
            "budget": "5",
            "dietary_filter": ""
        }
    )

    # Make sure the results page still loads successfully.
    assert response.status_code == 200

    # Make sure the backend uses "Beginner" as the default
    # experience level when the form does not include one.
    mock_get_recipes.assert_called_once_with(
        "pasta",
        "5",
        "Beginner",
        ""
    )

    # Make sure the returned page is actually the results page.
    assert b"Results" in response.data or b"ChefGPT" in response.data