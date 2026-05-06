"""
backend/auth_helper.py
Shared authentication helper used by route blueprints.
"""

from firebase_admin import auth as firebase_auth
from backend.firebase_init import FIREBASE_AVAILABLE


def verify_firebase_token(request):
    """
    Verifies Firebase ID token from Authorization header.

    Returns decoded user dict (uid, email, etc.) or None if invalid.
    """

    if not FIREBASE_AVAILABLE:
        return None

    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    id_token = auth_header.split("Bearer ", 1)[1]

    try:
        return firebase_auth.verify_id_token(id_token)
    except Exception:
        return None


# (optional backward compatibility)
get_current_user = verify_firebase_token