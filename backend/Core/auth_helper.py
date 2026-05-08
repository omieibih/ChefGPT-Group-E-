# =============================================================================
# auth_helper.py
#
# Provides a single helper function, get_current_user(), that extracts and
# verifies the Firebase ID token from an incoming Flask request's Authorization
# header. Returns the decoded user payload on success, or None on any failure,
# so callers can treat None as "not authenticated" without handling exceptions.
# =============================================================================

import logging  # Used to log token verification failures for debugging without crashing

from firebase_admin import auth as firebase_auth        # Firebase Admin SDK auth module for verifying tokens
from backend.Core.firebase_init import FIREBASE_AVAILABLE  # Flag set at startup; False if Firebase failed to init

# Create a logger named after this module so log output can be filtered by source
logger = logging.getLogger(__name__)


def get_current_user(request):
    # Skip verification entirely if Firebase never initialised successfully.
    # Returning None here causes all protected routes to respond with 401.
    if not FIREBASE_AVAILABLE:
        return None

    # Read the Authorization header; default to empty string if absent
    auth_header = request.headers.get("Authorization", "")
    # Firebase ID tokens must be sent as "Bearer <token>" — reject anything else
    if not auth_header.startswith("Bearer "):
        return None

    # Strip the "Bearer " prefix to isolate the raw token string
    id_token = auth_header.split("Bearer ", 1)[1]
    try:
        # Verify the token's signature, expiry, and audience against the Firebase project.
        # clock_skew_seconds=10 allows a 10-second tolerance for minor clock drift between
        # the client and server, preventing spurious "token expired" errors.
        return firebase_auth.verify_id_token(id_token, clock_skew_seconds=10)
    except Exception as exc:
        # Token was expired, revoked, malformed, or signed by the wrong project.
        # Log a warning so it's visible in server logs without raising an exception to the caller.
        logger.warning("Token verification failed: %s", exc)
        return None  # Treat any verification failure as unauthenticated
