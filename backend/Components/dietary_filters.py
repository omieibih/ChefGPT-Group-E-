def filter_recipes_by_diet(recipes, dietary_filter):
    valid_filters = ["vegan", "vegetarian", "gluten-free", "dairy-free", "nut-free"]

    if not recipes or not isinstance(recipes, list):
        return []

    if not dietary_filter or not isinstance(dietary_filter, str):
        return []

    dietary_filter = dietary_filter.strip().lower()

    if dietary_filter not in valid_filters:
        return []

    filtered_recipes = []

    for recipe in recipes:
        if not isinstance(recipe, dict):
            continue

        tags = recipe.get("dietary_tags", [])

        if isinstance(tags, str):
            tags = [tags]

        if not isinstance(tags, list):
            continue

        normalized_tags = [
            tag.strip().lower()
            for tag in tags
            if isinstance(tag, str)
        ]

        if dietary_filter in normalized_tags:
            filtered_recipes.append(recipe)

    return filtered_recipes