 # Function: filters a list of recipes based on a dietary restriction
def filter_recipes_by_diet(recipes, dietary_filter):
    
    # List of allowed/valid dietary filters to prevent invalid input
    valid_filters = ["vegan", "vegetarian", "gluten-free", "dairy-free", "nut-free"]

    # Reliability check:
    # If recipes is empty or not a list, return empty list to avoid crashes
    if not recipes or not isinstance(recipes, list):
        return []

    # Security + reliability:
    # Make sure dietary_filter exists and is a string
    if not dietary_filter or not isinstance(dietary_filter, str):
        return []

    # Normalize input:
    # Remove extra spaces and convert to lowercase for consistent comparison
    dietary_filter = dietary_filter.strip().lower()

    # Security:
    # Only allow known filters (prevents unexpected or malicious input)
    if dietary_filter not in valid_filters:
        return []

    # This will store the final filtered recipes
    filtered_recipes = []

    # Loop through each recipe in the list
    for recipe in recipes:

        # Reliability:
        # Skip anything that is not a dictionary (invalid recipe format)
        if not isinstance(recipe, dict):
            continue

        # Get dietary tags from the recipe (default to empty list if missing)
        tags = recipe.get("dietary_tags", [])

        # If tags is a single string, convert it to a list for consistency
        if isinstance(tags, str):
            tags = [tags]

        # Reliability:
        # If tags is not a list, skip this recipe
        if not isinstance(tags, list):
            continue

        # Normalize all tags:
        # - remove spaces
        # - convert to lowercase
        # - ignore non-string values
        normalized_tags = [
            tag.strip().lower() 
            for tag in tags 
            if isinstance(tag, str)
        ]

        # Check if the user's dietary filter matches any recipe tag
        if dietary_filter in normalized_tags:
            # If it matches, add recipe to results
            filtered_recipes.append(recipe)

    # Return the filtered list (could be empty if no matches found)
    return filtered_recipes