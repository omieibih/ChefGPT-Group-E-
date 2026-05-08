# =============================================================================
# firebase_init.py
#
# Initialises the Firebase Admin SDK exactly once when the module is first
# imported. Credentials are loaded from an environment variable (preferred for
# production/CI) or a local key file (convenient for local development).
#
# After import, other modules check FIREBASE_AVAILABLE before using Firebase.
# If initialisation failed, FIREBASE_INIT_ERROR holds the reason so it can be
# surfaced in API error responses rather than crashing silently.
# =============================================================================

import json                    # Used to parse the service account JSON stored in an env var
import os                      # Used to read environment variables and check file paths
from typing import Optional    # Allows FIREBASE_INIT_ERROR to be typed as str or None

import firebase_admin                    # The Firebase Admin SDK top-level package
from firebase_admin import credentials  # Provides the Certificate class for service-account auth

# Assume Firebase will initialise successfully; flipped to False in the except block below
FIREBASE_AVAILABLE: bool = True
# Stores the error message if initialisation fails; stays None on success
FIREBASE_INIT_ERROR: Optional[str] = None


def _load_firebase_credentials() -> credentials.Certificate:
    # First, try reading the entire service account JSON from an environment variable.
    # This is the preferred method in CI/CD and hosted environments where file access is restricted.
    key_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if key_json:
        # Parse the JSON string into a dict and wrap it in a Certificate object
        return credentials.Certificate(json.loads(key_json))

    # Fall back to a file path; default to "serviceAccountKey.json" in the project root
    key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    if os.path.exists(key_path):
        # Load the certificate directly from the file on disk
        return credentials.Certificate(key_path)

    # Neither source was available — raise so the caller knows exactly what to configure
    raise RuntimeError(
        "Firebase credentials not found. "
        "Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
    )


# Only initialise if no Firebase app has been registered yet.
# This guard prevents a duplicate-app error when the module is imported multiple times
# (e.g. during testing or hot-reload in development).
if not firebase_admin._apps:
    try:
        # Initialise the default Firebase app with the resolved credentials
        firebase_admin.initialize_app(_load_firebase_credentials())
    except Exception as _exc:
        # Initialisation failed (missing credentials, malformed JSON, network issue, etc.)
        FIREBASE_AVAILABLE = False       # Signal to the rest of the app that Firebase is down
        FIREBASE_INIT_ERROR = str(_exc)  # Capture the reason so routes can return a helpful 503
