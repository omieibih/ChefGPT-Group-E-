import json
import os
from typing import Optional

import firebase_admin
from firebase_admin import credentials

FIREBASE_AVAILABLE: bool = True
FIREBASE_INIT_ERROR: Optional[str] = None


def _load_firebase_credentials() -> credentials.Certificate:
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


if not firebase_admin._apps:
    try:
        firebase_admin.initialize_app(_load_firebase_credentials())
    except Exception as _exc:
        FIREBASE_AVAILABLE = False
        FIREBASE_INIT_ERROR = str(_exc)