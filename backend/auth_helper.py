"""
backend/auth_helper.py
Shared authentication helper used by every route blueprint that requires a
logged-in user.
"""

from firebase_admin import auth as firebase_auth
from backend.firebase_init import FIREBASE_AVAILABLE


def get_current_user(request):
    """
    Verifies the Firebase ID token supplied in the Authorization header.

    Returns the decoded token dict (contains uid, email, etc.) on success,
    or None when:
      - Firebase is not configured
      - The Authorization header is missing / malformed
      - The token is invalid or expired
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