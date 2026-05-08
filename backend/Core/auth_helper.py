import logging

from firebase_admin import auth as firebase_auth
from backend.Core.firebase_init import FIREBASE_AVAILABLE

logger = logging.getLogger(__name__)


def get_current_user(request):
    if not FIREBASE_AVAILABLE:
        return None

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    id_token = auth_header.split("Bearer ", 1)[1]
    try:
        return firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
    except Exception as exc:
        logger.warning("Token verification failed: %s", exc)
        return None