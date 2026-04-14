from firebase_admin import firestore

# This file handles all Firebase Firestore operations for saving,
# retrieving, and deleting favorite recipes.

def save_favorite(user, data):
    db_firestore = firestore.client()
    db_firestore.collection("favorites").add({
        "uid": user["uid"],
        "name": data.get("name"),
        "ingredients": data.get("ingredients"),
        "instructions": data.get("instructions"),
    })

def get_favorites(user):
    db_firestore = firestore.client()
    docs = db_firestore.collection("favorites").where("uid", "==", user["uid"]).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

def delete_favorite(doc_id):
    db_firestore = firestore.client()
    db_firestore.collection("favorites").document(doc_id).delete()