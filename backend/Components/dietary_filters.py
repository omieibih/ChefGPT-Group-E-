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
#
# These comments connect to:
# - Ticket 3 Code Management (branching, merging, reviewing code) :contentReference[oaicite:0]{index=0}
# - Ticket 4 Architecture Design (separation of concerns and maintainability) :contentReference[oaicite:1]{index=1}
# - Testing and code readability activities from Weeks 7, 8, and 15 :contentReference[oaicite:2]{index=2}
# - Assignment 2 Test Case development and defensive programming concepts :contentReference[oaicite:3]{index=3}


def filter_recipes_by_diet(recipes, dietary_filter):
    valid_filters = ["vegan", "vegetarian", "gluten-free", "dairy-free", "nut-free"]

    if not recipes or not isinstance(recipes, list):
        return []

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

    filtered_recipes = []

    # Loop through each recipe in the recipe list.
    for recipe in recipes:
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

        normalized_tags = [
            tag.strip().lower()
            for tag in tags
            if isinstance(tag, str)
        ]

        if dietary_filter in normalized_tags:
            filtered_recipes.append(recipe)

    return filtered_recipes