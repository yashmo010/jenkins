import tempfile
import unittest
from pathlib import Path

from app import create_app


class HospitalAppTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database = str(Path(self.temp_dir.name) / "test.db")
        self.app = create_app(
            {
                "TESTING": True,
                "DATABASE": database,
                "SECRET_KEY": "test-key",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def add_patient(self, name="Taylor Reed"):
        return self.client.post(
            "/patients",
            data={"name": name, "age": "31", "phone": "555-0100"},
            follow_redirects=True,
        )

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_dashboard_and_seeded_staff_load(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Doctors on staff", response.data)
        self.add_patient()
        self.assertIn(b"Dr. Maya Patel", self.client.get("/appointments").data)

    def test_patient_can_be_added_and_searched(self):
        response = self.add_patient()
        self.add_patient("Jordan Lee")
        self.assertIn(b"Patient added.", response.data)
        search = self.client.get("/patients?q=Taylor")
        self.assertIn(b"Taylor Reed", search.data)
        self.assertNotIn(b"Jordan Lee", search.data)

    def test_invalid_patient_is_not_saved(self):
        response = self.client.post(
            "/patients",
            data={"name": "", "age": "999"},
            follow_redirects=True,
        )
        self.assertIn(b"Enter a name and a valid age", response.data)
        self.assertIn(b"No patients found", response.data)

    def test_appointment_requires_valid_patient_and_date(self):
        self.add_patient()
        response = self.client.post(
            "/appointments",
            data={
                "patient_id": "1",
                "doctor_id": "1",
                "appointment_at": "not-a-date",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Choose a patient, doctor, date and time", response.data)
        self.assertIn(b"No appointments yet", response.data)

    def test_appointment_can_be_scheduled(self):
        self.add_patient()
        response = self.client.post(
            "/appointments",
            data={
                "patient_id": "1",
                "doctor_id": "1",
                "appointment_at": "2030-04-15T10:30",
                "reason": "Routine check-up",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Appointment scheduled.", response.data)
        self.assertIn(b"Routine check-up", response.data)


if __name__ == "__main__":
    unittest.main()
