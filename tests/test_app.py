import unittest
from datetime import date, timedelta

from app import create_app


class InsertResult:
    inserted_id = "test-id-123"


class FakeBookingsCollection:
    def __init__(self):
        self.documents = []

    def insert_one(self, document):
        self.documents.append(document)
        return InsertResult()


class TrailQuestTests(unittest.TestCase):
    def setUp(self):
        self.collection = FakeBookingsCollection()
        self.app = create_app({"TESTING": True, "BOOKINGS_COLLECTION": self.collection})
        self.client = self.app.test_client()

    def valid_payload(self):
        return {
            "name": "Rahul Sharma",
            "email": "rahul@example.com",
            "phone": "9876543210",
            "destination": "Manali",
            "travelers": 2,
            "travel_date": (date.today() + timedelta(days=10)).isoformat(),
            "message": "Interested in trekking.",
        }

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"KARAN", response.data)
        self.assertIn(b"TRAILQUEST", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "healthy")

    def test_tours_api(self):
        response = self.client.get("/api/tours")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.get_json()["tours"]), 6)

    def test_valid_booking_is_saved(self):
        response = self.client.post("/api/bookings", json=self.valid_payload())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(self.collection.documents), 1)
        self.assertEqual(self.collection.documents[0]["phone"], "9876543210")
        self.assertEqual(self.collection.documents[0]["status"], "pending")

    def test_invalid_email_is_rejected(self):
        payload = self.valid_payload()
        payload["email"] = "rahulexample.com"
        response = self.client.post("/api/bookings", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.get_json()["errors"])

    def test_phone_must_be_exactly_ten_digits(self):
        payload = self.valid_payload()
        payload["phone"] = "12345"
        response = self.client.post("/api/bookings", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.get_json()["errors"])

    def test_past_date_is_rejected(self):
        payload = self.valid_payload()
        payload["travel_date"] = (date.today() - timedelta(days=1)).isoformat()
        response = self.client.post("/api/bookings", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("travel_date", response.get_json()["errors"])


if __name__ == "__main__":
    unittest.main()
