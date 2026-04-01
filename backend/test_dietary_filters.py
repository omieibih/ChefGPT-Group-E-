import unittest
from backend.dietary_filters import DietaryFilter

class TestDietaryFilter(unittest.TestCase):

    def setUp(self):
        self.filter = DietaryFilter()

    def test_apply_filter_removes_items(self):
        ingredients = ["chicken", "milk", "rice"]
        restrictions = ["milk"]
        result = self.filter.apply_filter(ingredients, restrictions)
        self.assertEqual(result, ["chicken", "rice"])

    def test_apply_filter_none(self):
        result = self.filter.apply_filter(None, None)
        self.assertEqual(result, [])

    def test_apply_filter_empty_restrictions(self):
        result = self.filter.apply_filter(["rice"], [])
        self.assertEqual(result, ["rice"])

if __name__ == "__main__":
    unittest.main()