import unittest
from unittest.mock import patch, MagicMock
import json
import app


class TestShoppingListPage(unittest.TestCase):

    def test_shopping_page_loads(self):
        """GET /shopping-list should return 200 OK"""
        tester = app.app.test_client(self)
        response = tester.get("/shopping-list")
        self.assertEqual(response.status_code, 200)


class TestGetShoppingListItems(unittest.TestCase):

    @patch("backend.Components.shopping_list.firestore")
    @patch("backend.Components.shopping_list.get_current_user")
    def test_get_items_returns_list(self, mock_auth, mock_firestore):
        """GET /api/shopping-list should return a JSON array for authenticated user"""
        mock_auth.return_value = {"uid": "user123"}

        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"name": "Milk", "completed": False}
        mock_doc.id = "doc1"

        mock_firestore.client.return_value.collection.return_value \
            .document.return_value.collection.return_value \
            .stream.return_value = [mock_doc]

        tester = app.app.test_client(self)
        response = tester.get("/api/shopping-list", headers={"Authorization": "Bearer token"})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    @patch("backend.Components.shopping_list.firestore")
    @patch("backend.Components.shopping_list.get_current_user")
    def test_get_items_contains_expected_fields(self, mock_auth, mock_firestore):
        """Each item in the list should have id, name, and completed fields"""
        mock_auth.return_value = {"uid": "user123"}

        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {"name": "Eggs", "completed": False}
        mock_doc.id = "doc42"

        mock_firestore.client.return_value.collection.return_value \
            .document.return_value.collection.return_value \
            .stream.return_value = [mock_doc]

        tester = app.app.test_client(self)
        response = tester.get("/api/shopping-list", headers={"Authorization": "Bearer token"})

        item = json.loads(response.data)[0]
        self.assertIn("id", item)
        self.assertIn("name", item)
        self.assertIn("completed", item)
        self.assertEqual(item["id"], "doc42")
        self.assertEqual(item["name"], "Eggs")

    @patch("backend.Components.shopping_list.get_current_user")
    def test_get_items_unauthorized(self, mock_auth):
        """GET /api/shopping-list should return 401 if user is not authenticated"""
        mock_auth.return_value = None

        tester = app.app.test_client(self)
        response = tester.get("/api/shopping-list")

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch("backend.Components.shopping_list.firestore")
    @patch("backend.Components.shopping_list.get_current_user")
    def test_get_items_empty_list(self, mock_auth, mock_firestore):
        """GET /api/shopping-list should return an empty array when no items exist"""
        mock_auth.return_value = {"uid": "user123"}

        mock_firestore.client.return_value.collection.return_value \
            .document.return_value.collection.return_value \
            .stream.return_value = []

        tester = app.app.test_client(self)
        response = tester.get("/api/shopping-list", headers={"Authorization": "Bearer token"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])


class TestAddShoppingListItem(unittest.TestCase):

    @patch("backend.Components.shopping_list.firestore")
    @patch("backend.Components.shopping_list.get_current_user")
    def test_add_item_returns_item_with_id(self, mock_auth, mock_firestore):
        """POST /api/shopping-list should return the new item including its generated id"""
        mock_auth.return_value = {"uid": "user123"}

        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "new_doc_id"
        mock_firestore.client.return_value.collection.return_value \
            .document.return_value.collection.return_value \
            .add.return_value = (None, mock_doc_ref)

        tester = app.app.test_client(self)
        response = tester.post(
            "/api/shopping-list",
            json={"name": "Butter"},
            headers={"Authorization": "Bearer token"},
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["name"], "Butter")
        self.assertEqual(data["id"], "new_doc_id")
        self.assertFalse(data["completed"])

    @patch("backend.Components.shopping_list.firestore")
    @patch("backend.Components.shopping_list.get_current_user")
    def test_add_item_completed_defaults_to_false(self, mock_auth, mock_firestore):
        """Newly added items should always have completed set to False"""
        mock_auth.return_value = {"uid": "user123"}

        mock_doc_ref = MagicMock()
        mock_doc_ref.id = "abc"
        mock_firestore.client.return_value.collection.return_value \
            .document.return_value.collection.return_value \
            .add.return_value = (None, mock_doc_ref)

        tester = app.app.test_client(self)
        response = tester.post(
            "/api/shopping-list",
            json={"name": "Bread"},
            headers={"Authorization": "Bearer token"},
        )

        data = json.loads(response.data)
        self.assertFalse(data["completed"])

    @patch("backend.Components.shopping_list.get_current_user")
    def test_add_item_unauthorized(self, mock_auth):
        """POST /api/shopping-list should return 401 if user is not authenticated"""
        mock_auth.return_value = None

        tester = app.app.test_client(self)
        response = tester.post(
            "/api/shopping-list",
            json={"name": "Cheese"},
        )

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)


class TestDeleteShoppingListItem(unittest.TestCase):

    @patch("backend.Components.shopping_list.firestore")
    @patch("backend.Components.shopping_list.get_current_user")
    def test_delete_item_returns_success(self, mock_auth, mock_firestore):
        """DELETE /api/shopping-list/<doc_id> should return {success: true}"""
        mock_auth.return_value = {"uid": "user123"}

        mock_firestore.client.return_value.collection.return_value \
            .document.return_value.collection.return_value \
            .document.return_value.delete.return_value = None

        tester = app.app.test_client(self)
        response = tester.delete(
            "/api/shopping-list/doc1",
            headers={"Authorization": "Bearer token"},
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data["success"])

    @patch("backend.Components.shopping_list.get_current_user")
    def test_delete_item_unauthorized(self, mock_auth):
        """DELETE /api/shopping-list/<doc_id> should return 401 if user is not authenticated"""
        mock_auth.return_value = None

        tester = app.app.test_client(self)
        response = tester.delete("/api/shopping-list/doc1")

        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
