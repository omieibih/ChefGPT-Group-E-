import unittest
from backend.dietary_filters import filter_recipes_by_diet

class TestDietaryFilter(unittest.TestCase):

    def test_valid_filter(self):
        recipes = [
            {"name": "Vegan Pasta", "dietary_tags": ["vegan", "dairy-free"]},
            {"name": "Chicken Salad", "dietary_tags": ["gluten-free"]}
        ]
        result = filter_recipes_by_diet(recipes, "vegan")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Vegan Pasta")

    def test_invalid_filter(self):
        recipes = [
            {"name": "Vegan Pasta", "dietary_tags": ["vegan"]}
        ]
        result = filter_recipes_by_diet(recipes, "keto")
        self.assertEqual(result, [])

    def test_empty_input(self):
        result = filter_recipes_by_diet([], "")
        self.assertEqual(result, [])

    def test_none_input(self):
        result = filter_recipes_by_diet(None, None)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()