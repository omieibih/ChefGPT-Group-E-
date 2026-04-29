"""
app.py
Application entry point.

Responsibilities
----------------
- Create the Flask app instance
- Load environment variables
- Register all feature blueprints
- Start the dev server when run directly

All business logic lives in backend/routes/*.py and backend/*.py.
"""

import os

from dotenv import load_dotenv
from flask import Flask

# Load .env before any other import that reads env vars.
load_dotenv()

# Firebase is initialised as a side-effect of this import so it happens once,
# before any blueprint tries to use it.
import backend.firebase_init  # noqa: F401

from backend.routes import all_blueprints

app = Flask(__name__)

for blueprint in all_blueprints:
    app.register_blueprint(blueprint)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)