#beginn
class DietaryFilter:

    def apply_filter(self, ingredients, restrictions):
        if ingredients is None or restrictions is None:
            return []

        return [item for item in ingredients if item not in restrictions]