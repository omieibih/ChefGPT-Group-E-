
# Dietary Filter Feature
# ChefGPT - CS3203
#
# Purpose:
# This function filters recipes based on a user's dietary restriction.
#
# Related CWE:
# CWE-703: Improper Check or Handling of Exceptional Conditions
#
# This function addresses CWE-703 by validating inputs before processing them.
# Instead of crashing when invalid or unexpected data is passed in,
# the function safely returns an empty list or skips invalid entries.
#
# Security:
# - Only approved dietary filters are allowed.
# - User input is normalized before comparison.
# - Invalid data types are rejected safely.
#
# Reliability:
# - Handles empty inputs and incorrect data structures.
# - Prevents runtime errors caused by invalid recipe/tag formats.
# - Uses safe checks before accessing or looping through data.
#
# Architecture:
# - Dietary filtering logic is separated into its own helper function.
# - Keeps filtering independent from Flask routes and UI logic.
# - Makes the feature easier to maintain and test.
#
# Complexity:
# - Uses early returns to reduce nested logic.
# - Keeps filtering decisions grouped together.
# - Breaks filtering into simple readable steps.
#
# Related class activities:
# - Reliability planning
# - Refactoring and reducing complexity
# - Secure input validation
# - Architecture separation of concerns
# - Defensive programming practices
def filter_recipes_by_diet(recipes, dietary_filter):
    # List of allowed dietary filters.
    # Security:
    # Only approved dietary filters can be processed.
    valid_filters = ["vegan", "vegetarian", "gluten-free", "dairy-free", "nut-free"]
    
    # Reliability / CWE-703:
    # Make sure recipes exists and is a list before processing.
    # Prevents crashes from invalid or missing recipe data.
    if not recipes or not isinstance(recipes, list):
        return []
   
    # Reliability / Security:
    # Make sure dietary_filter exists and is a string.
    # Prevents invalid input types from causing errors.
    if not dietary_filter or not isinstance(dietary_filter, str):
        return []

    # Normalize the user input.
    # Removes extra spaces and converts text to lowercase
    # so comparisons stay consistent.
    dietary_filter = dietary_filter.strip().lower()

    # Security:
    # Reject unsupported dietary filters.
    # Prevents unexpected or invalid filter values.
    if dietary_filter not in valid_filters:
        return []

    # Stores recipes that match the dietary restriction.
    filtered_recipes = []

    # Loop through each recipe in the recipe list.
    for recipe in recipes:

        # Reliability / CWE-703:
        # Ensure each recipe is a dictionary before accessing values.
        # Skip invalid recipe entries safely.
        if not isinstance(recipe, dict):
            continue

        # Get dietary tags from the recipe.
        # Default to an empty list if tags are missing.
        tags = recipe.get("dietary_tags", [])

        # Reliability:
        # Convert a single string tag into a list
        # so all recipes use the same structure.
        if isinstance(tags, str):
            tags = [tags]

        # Reliability / Defensive Programming:
        # Skip recipes with invalid tag structures.
        if not isinstance(tags, list):
            continue

        # Normalize all dietary tags.
        # - remove spaces
        # - convert to lowercase
        # - ignore non-string values
        #
        # Complexity reduction:
        # Keeps all normalization logic in one place.

        normalized_tags = [
            tag.strip().lower()
            for tag in tags
            if isinstance(tag, str)
        ]


        if dietary_filter in normalized_tags:
            filtered_recipes.append(recipe)


        # Filtering logic:
        # If the user's dietary restriction matches a recipe tag,
        # add the recipe to the filtered list.
        if dietary_filter in normalized_tags:
            filtered_recipes.append(recipe)

    # Return the final filtered recipes list.
    # May return an empty list if no recipes match.

    return filtered_recipes