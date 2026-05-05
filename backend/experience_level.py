from firebase_admin import firestore


def save_experience_level(user, experience_level):
    """
    Saves or updates the cooking experience level for the authenticated user.
    """
    db_firestore = firestore.client()

    db_firestore.collection("users").document(user["uid"]).set(
        {
            "uid": user["uid"],
            "email": user.get("email"),
            "experience_level": experience_level,
        },
        merge=True,
    )


def get_experience_level(user):
    """
    Returns the saved cooking experience level for the authenticated user.
    Defaults to Beginner if no level has been saved yet.
    """
    db_firestore = firestore.client()
    doc = db_firestore.collection("users").document(user["uid"]).get()

    if not doc.exists:
        return "Beginner"

    data = doc.to_dict() or {}
    return data.get("experience_level", "Beginner")