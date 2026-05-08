import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to Python path
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app import app


# =========================================================
# SHOPPING LIST TESTS
# =========================================================

# Flask test client
tester = app.test_client()


# =========================================================
# TEST 1
# Shopping page loads correctly
# =========================================================
def test_shopping_page_loads():

    response = tester.get("/shopping-list")

    assert response.status_code == 200


# =========================================================
# TEST 2
# Add shopping list item
# =========================================================
@patch("backend.routes.shopping_List.verify_firebase_token")
@patch("backend.routes.shopping_List.db")
def test_add_item(mock_db, mock_verify):

    # Fake logged-in user
    mock_verify.return_value = {
        "uid": "test-user"
    }

    # Fake Firestore response
    fake_doc = MagicMock()
    fake_doc.id = "abc123"

    mock_db.collection.return_value \
        .document.return_value \
        .collection.return_value \
        .add.return_value = (None, fake_doc)

    # Send POST request
    response = tester.post(
        "/api/shopping-list",
        json={
            "name": "milk"
        }
    )

    # Convert response JSON
    data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert data["name"] == "milk"
    assert data["completed"] is False
    assert data["id"] == "abc123"


# =========================================================
# TEST 3
# Get shopping list items
# =========================================================
@patch("backend.routes.shopping_List.verify_firebase_token")
@patch("backend.routes.shopping_List.db")
def test_get_items(mock_db, mock_verify):

    # Fake logged-in user
    mock_verify.return_value = {
        "uid": "test-user"
    }

    # Fake Firestore documents
    fake_doc = MagicMock()

    fake_doc.id = "item1"

    fake_doc.to_dict.return_value = {
        "name": "eggs",
        "completed": False
    }

    mock_db.collection.return_value \
        .document.return_value \
        .collection.return_value \
        .stream.return_value = [fake_doc]

    # Send GET request
    response = tester.get("/api/shopping-list")

    data = response.get_json()

    # Assertions
    assert response.status_code == 200

    assert len(data) == 1

    assert data[0]["name"] == "eggs"


# =========================================================
# TEST 4
# Delete shopping list item
# =========================================================
@patch("backend.routes.shopping_List.verify_firebase_token")
@patch("backend.routes.shopping_List.db")
def test_delete_item(mock_db, mock_verify):

    # Fake logged-in user
    mock_verify.return_value = {
        "uid": "test-user"
    }

    # Send DELETE request
    response = tester.delete(
        "/api/shopping-list/item123"
    )

    data = response.get_json()

    # Assertions
    assert response.status_code == 200

    assert data["success"] is True