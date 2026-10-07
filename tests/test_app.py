import unittest
from unittest.mock import patch
import app as app_module

class FakeCursor:
    def __init__(self, rows=None):
        self.rows = rows or []
    def sort(self, *args, **kwargs):
        return self
    def __iter__(self):
        return iter(self.rows)

class FakeCollection:
    def __init__(self, rows=None):
        self.rows = rows or []
    def find(self, *args, **kwargs):
        return FakeCursor(self.rows)
    def update_one(self, *args, **kwargs):
        return None

class FakeDatabase:
    def __init__(self, skills=None, pipeline=None):
        self.skills = FakeCollection(skills)
        self.pipeline_stages = FakeCollection(pipeline)

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Karan DevOps Dashboard", response.data)

    @patch("app.initialize_database")
    @patch("app.check_database", return_value=True)
    def test_health(self, mock_check_database, mock_initialize_database):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["database_type"], "MongoDB Atlas")

    @patch("app.check_database", return_value=True)
    def test_api_status(self, mock_check_database):
        response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "running")
        self.assertEqual(data["database"], "connected")
        self.assertEqual(data["database_type"], "MongoDB Atlas")

    @patch("app.initialize_database")
    @patch("app.get_db", return_value=FakeDatabase(
        skills=[
            {"name": "Linux", "level": 82},
            {"name": "Docker", "level": 80},
            {"name": "Kubernetes", "level": 68},
        ]
    ))
    def test_api_skills(self, mock_get_db, mock_initialize_database):
        response = self.client.get("/api/skills")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["skills"]), 3)
        self.assertEqual(data["skills"][0]["name"], "Linux")

    @patch("app.initialize_database")
    @patch("app.get_db", return_value=FakeDatabase(
        pipeline=[
            {"stage": "Checkout", "status": "success", "description": "Source code downloaded from GitHub"},
            {"stage": "Docker Build", "status": "success", "description": "Docker image built successfully"},
            {"stage": "Kubernetes Deploy", "status": "success", "description": "Application deployed to Kubernetes"},
        ]
    ))
    def test_api_pipeline(self, mock_get_db, mock_initialize_database):
        response = self.client.get("/api/pipeline")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["pipeline"]), 3)
        self.assertEqual(data["pipeline"][0]["stage"], "Checkout")

if __name__ == "__main__":
    unittest.main()
