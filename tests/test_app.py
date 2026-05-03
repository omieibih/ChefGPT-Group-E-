import unittest
from unittest.mock import patch, MagicMock
import json
import app


class TestChefGPT(unittest.TestCase):

    # -------------------------
    # Route Tests
    # -------------------------

    def test_home_page_loads(self):
        """Home page should return 200 OK"""
        tester = app.app.test_client(self)
        response = tester.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_contains_form(self):
        """Home page should contain the ingredient input form"""
        tester = app.app.test_client(self)
        response = tester.get("/")
        self.assertIn(b"ingredients", response.data)

    def test_results_page_requires_post(self):
        """Results page should not be accessible via GET"""
        tester = app.app.test_client(self)
        response = tester.get("/results")
        self.assertEqual(response.status_code, 405)

    # -------------------------
    # get_recipes() Unit Tests
    # -------------------------

    @patch("app.Groq")
    def test_get_recipes_returns_three_meals(self, mock_groq):
        """get_recipes should return a list of exactly 3 meals"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "name": "Chicken Stir Fry",
                "description": "A quick stir fry.",
                "core_ingredients": ["chicken", "rice"],
                "additional_ingredients": ["soy sauce (~$2)"],
                "instructions": ["Step 1: Cook chicken.", "Step 2: Add rice."]
            },
            {
                "name": "Chicken Soup",
                "description": "A warm soup.",
                "core_ingredients": ["chicken"],
                "additional_ingredients": ["broth (~$3)"],
                "instructions": ["Step 1: Boil chicken.", "Step 2: Add broth."]
            },
            {
                "name": "Chicken Pasta",
                "description": "A creamy pasta.",
                "core_ingredients": ["chicken"],
                "additional_ingredients": ["pasta (~$2)"],
                "instructions": ["Step 1: Cook pasta.", "Step 2: Add chicken."]
            }
        ])
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        result = app.get_recipes("chicken, rice", "20")
        self.assertEqual(len(result), 3)

    @patch("app.Groq")
    def test_get_recipes_meal_has_required_fields(self, mock_groq):
        """Each meal should contain name, description, core_ingredients, additional_ingredients, and instructions"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "name": "Chicken Stir Fry",
                "description": "A quick stir fry.",
                "core_ingredients": ["chicken", "rice"],
                "additional_ingredients": ["soy sauce (~$2)"],
                "instructions": ["Step 1: Cook chicken."]
            },
            {
                "name": "Chicken Soup",
                "description": "A warm soup.",
                "core_ingredients": ["chicken"],
                "additional_ingredients": ["broth (~$3)"],
                "instructions": ["Step 1: Boil chicken."]
            },
            {
                "name": "Chicken Pasta",
                "description": "A creamy pasta.",
                "core_ingredients": ["chicken"],
                "additional_ingredients": ["pasta (~$2)"],
                "instructions": ["Step 1: Cook pasta."]
            }
        ])
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        result = app.get_recipes("chicken", "10")
        for meal in result:
            self.assertIn("name", meal)
            self.assertIn("description", meal)
            self.assertIn("core_ingredients", meal)
            self.assertIn("additional_ingredients", meal)
            self.assertIn("instructions", meal)

    @patch("app.Groq")
    def test_get_recipes_with_no_budget(self, mock_groq):
        """get_recipes should work fine when no budget is provided"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "name": "Egg Fried Rice",
                "description": "Simple fried rice.",
                "core_ingredients": ["egg", "rice"],
                "additional_ingredients": [],
                "instructions": ["Step 1: Fry egg.", "Step 2: Add rice."]
            },
            {
                "name": "Egg Soup",
                "description": "Light egg soup.",
                "core_ingredients": ["egg"],
                "additional_ingredients": [],
                "instructions": ["Step 1: Boil water.", "Step 2: Add egg."]
            },
            {
                "name": "Scrambled Eggs",
                "description": "Classic scrambled eggs.",
                "core_ingredients": ["egg"],
                "additional_ingredients": [],
                "instructions": ["Step 1: Beat eggs.", "Step 2: Cook in pan."]
            }
        ])
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        result = app.get_recipes("egg, rice", "")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    @patch("app.Groq")
    def test_get_recipes_returns_list(self, mock_groq):
        """get_recipes should return a list, not a dict or string"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "name": "Meal 1",
                "description": "Desc 1",
                "core_ingredients": ["a"],
                "additional_ingredients": [],
                "instructions": ["Step 1"]
            },
            {
                "name": "Meal 2",
                "description": "Desc 2",
                "core_ingredients": ["b"],
                "additional_ingredients": [],
                "instructions": ["Step 1"]
            },
            {
                "name": "Meal 3",
                "description": "Desc 3",
                "core_ingredients": ["c"],
                "additional_ingredients": [],
                "instructions": ["Step 1"]
            }
        ])
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        result = app.get_recipes("pasta", "15")
        self.assertIsInstance(result, list)

    @patch("app.Groq")
    def test_get_recipes_instructions_is_list(self, mock_groq):
        """Instructions for each meal should be a list"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps([
            {
                "name": "Taco",
                "description": "Simple taco.",
                "core_ingredients": ["beef"],
                "additional_ingredients": ["taco shells (~$3)"],
                "instructions": ["Step 1: Cook beef.", "Step 2: Fill shells."]
            },
            {
                "name": "Beef Bowl",
                "description": "Rice bowl.",
                "core_ingredients": ["beef", "rice"],
                "additional_ingredients": [],
                "instructions": ["Step 1: Cook rice.", "Step 2: Add beef."]
            },
            {
                "name": "Beef Stew",
                "description": "Hearty stew.",
                "core_ingredients": ["beef"],
                "additional_ingredients": ["potatoes (~$2)"],
                "instructions": ["Step 1: Brown beef.", "Step 2: Add potatoes."]
            }
        ])
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        result = app.get_recipes("beef, rice", "10")
        for meal in result:
            self.assertIsInstance(meal["instructions"], list)

    # -------------------------
    # Error Handling Tests
    # -------------------------

    @patch("app.Groq")
    def test_results_page_shows_error_on_api_failure(self, mock_groq):
        """Results page should display error message if API call fails"""
        mock_groq.return_value.chat.completions.create.side_effect = Exception("API error")

        tester = app.app.test_client(self)
        response = tester.post("/results", data={
            "ingredients": "chicken",
            "budget": "10"
        })
        self.assertIn(b"Something went wrong", response.data)

    @patch("app.Groq")
    def test_get_recipes_raises_on_invalid_json(self, mock_groq):
        """get_recipes should raise an error if API returns invalid JSON"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is not valid JSON"
        mock_groq.return_value.chat.completions.create.return_value = mock_response

        with self.assertRaises(Exception):
            app.get_recipes("chicken", "10")


if __name__ == "__main__":
    unittest.main()