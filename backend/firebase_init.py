"""
backend/firebase_init.py
Initializes the Firebase Admin SDK exactly once and exposes two module-level
constants that every other backend module can import:

    FIREBASE_AVAILABLE  – bool, False when credentials are missing/broken
    FIREBASE_INIT_ERROR – str | None, human-readable error if unavailable
"""

import json
import os

import firebase_admin
from firebase_admin import credentials

FIREBASE_AVAILABLE: bool = True
FIREBASE_INIT_ERROR: str | None = None


def _load_firebase_credentials() -> credentials.Certificate:
    """
    Load Firebase Admin credentials from environment variables or a local
    fallback file.  Keeps secrets out of source control (addresses CWE-798).

    Priority:
      1. FIREBASE_SERVICE_ACCOUNT_JSON  – full JSON string (ideal for prod)
      2. FIREBASE_SERVICE_ACCOUNT_PATH  – path to a local key file (dev)
    """
    key_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")
    if key_json:
        return credentials.Certificate(json.loads(key_json))

    key_path = os.environ.get("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")
    if os.path.exists(key_path):
        return credentials.Certificate(key_path)

    raise RuntimeError(
        "Firebase credentials not found. "
        "Set FIREBASE_SERVICE_ACCOUNT_JSON or FIREBASE_SERVICE_ACCOUNT_PATH."
    )


# Initialize only once – guard against double-import in testing environments.
if not firebase_admin._apps:
    try:
        firebase_admin.initialize_app(_load_firebase_credentials())
    except Exception as _exc:
        FIREBASE_AVAILABLE = False
        FIREBASE_INIT_ERROR = str(_exc)