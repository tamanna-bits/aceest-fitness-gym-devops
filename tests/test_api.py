import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

@pytest.fixture
def client():
    """Create a fresh Flask test client for every test."""
    app = create_app({"TESTING": True})
    import app.routes as gym_routes
    gym_routes.members.clear()
    with app.test_client() as c:
        yield c


# ── Health / Home ────────────────────────────────────────────────────────
class TestHome:
    def test_home_returns_200(self, client):
        res = client.get("/")
        assert res.status_code == 200

    def test_home_message(self, client):
        res = client.get("/")
        assert res.get_json()["message"] == "ACEest Fitness & Gym API Running"

    def test_health_returns_200(self, client):
        res = client.get("/health")
        assert res.status_code == 200

    def test_health_status(self, client):
        res = client.get("/health")
        assert res.get_json()["status"] == "healthy"


# ── Add Member ───────────────────────────────────────────────────────────
class TestAddMember:
    # VIP can access any program; using "Muscle Gain (MG)" here
    VALID = {"name": "Arjun", "age": 25, "membership": "VIP", "program": "Muscle Gain (MG)"}

    def test_add_member_returns_201(self, client):
        res = client.post("/members", json=self.VALID)
        assert res.status_code == 201

    def test_add_member_returns_correct_name(self, client):
        res = client.post("/members", json=self.VALID)
        assert res.get_json()["name"] == "Arjun"

    def test_add_member_assigns_id(self, client):
        res = client.post("/members", json=self.VALID)
        assert res.get_json()["id"] == 1

    def test_add_member_increments_id(self, client):
        client.post("/members", json=self.VALID)
        # Premium can access "Fat Loss (FL)" and "Beginner (BG)"
        second = {"name": "Priya", "age": 22, "membership": "Premium", "program": "Fat Loss (FL)"}
        res = client.post("/members", json=second)
        assert res.get_json()["id"] == 2

    def test_add_member_calories_calculated(self, client):
        """Calories = weight * calorie_factor; Muscle Gain factor is 35."""
        payload = {**self.VALID, "weight": 80}
        res = client.post("/members", json=payload)
        assert res.get_json()["calories"] == 80 * 35

    def test_add_member_default_weight(self, client):
        """Weight defaults to 70 when not provided."""
        res = client.post("/members", json=self.VALID)
        assert res.get_json()["weight"] == 70

    def test_add_member_missing_name_returns_400(self, client):
        res = client.post("/members", json={"age": 25, "membership": "Basic", "program": "Beginner (BG)"})
        assert res.status_code == 400

    def test_add_member_missing_age_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "membership": "VIP", "program": "Muscle Gain (MG)"})
        assert res.status_code == 400

    def test_add_member_missing_program_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "age": 25, "membership": "VIP"})
        assert res.status_code == 400

    def test_add_member_invalid_membership_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "age": 20, "membership": "Unknown", "program": "Beginner (BG)"})
        assert res.status_code == 400

    def test_add_member_invalid_program_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "age": 20, "membership": "VIP", "program": "NonExistent"})
        assert res.status_code == 400

    def test_add_member_program_not_allowed_for_membership_returns_403(self, client):
        """Basic members cannot enrol in Fat Loss or Muscle Gain programs."""
        res = client.post("/members", json={"name": "X", "age": 20, "membership": "Basic", "program": "Fat Loss (FL)"})
        assert res.status_code == 403

    def test_add_member_negative_age_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "age": -5, "membership": "VIP", "program": "Muscle Gain (MG)"})
        assert res.status_code == 400

    def test_add_member_no_body_returns_400(self, client):
        res = client.post("/members", content_type="application/json", data="")
        assert res.status_code == 400


# ── Get Members ──────────────────────────────────────────────────────────
class TestGetMembers:
    def test_get_members_empty(self, client):
        res = client.get("/members")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_get_members_after_add(self, client):
        # Basic membership can only access "Beginner (BG)"
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Basic", "program": "Beginner (BG)"})
        res = client.get("/members")
        assert len(res.get_json()) == 1

    def test_get_members_multiple(self, client):
        for i in range(3):
            client.post("/members", json={"name": f"User{i}", "age": 20 + i, "membership": "VIP", "program": "Muscle Gain (MG)"})
        res = client.get("/members")
        assert len(res.get_json()) == 3


# ── Get Single Member ────────────────────────────────────────────────────
class TestGetMember:
    def test_get_existing_member(self, client):
        # Premium can access "Fat Loss (FL)"
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Premium", "program": "Fat Loss (FL)"})
        res = client.get("/members/1")
        assert res.status_code == 200
        assert res.get_json()["name"] == "Arjun"

    def test_get_nonexistent_member_returns_404(self, client):
        res = client.get("/members/999")
        assert res.status_code == 404


# ── Update Member ────────────────────────────────────────────────────────
class TestUpdateMember:
    def test_update_member_age(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "VIP", "program": "Muscle Gain (MG)"})
        res = client.put("/members/1", json={"age": 30})
        assert res.status_code == 200
        assert res.get_json()["age"] == 30

    def test_update_nonexistent_member_returns_404(self, client):
        res = client.put("/members/999", json={"age": 30})
        assert res.status_code == 404

    def test_update_does_not_change_id(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "VIP", "program": "Muscle Gain (MG)"})
        res = client.put("/members/1", json={"id": 99, "age": 30})
        assert res.get_json()["id"] == 1


# ── Delete Member ────────────────────────────────────────────────────────
class TestDeleteMember:
    def test_delete_member_returns_200(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Basic", "program": "Beginner (BG)"})
        res = client.delete("/members/1")
        assert res.status_code == 200

    def test_delete_removes_member(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Premium", "program": "Fat Loss (FL)"})
        client.delete("/members/1")
        res = client.get("/members")
        assert res.get_json() == []

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/members/999")
        assert res.status_code == 404


# ── Calorie Calculator ───────────────────────────────────────────────────
class TestCalcCalories:
    def test_valid_program_and_weight(self, client):
        res = client.get("/programs/Beginner (BG)/calories?weight=70")
        assert res.status_code == 200
        data = res.get_json()
        assert data["calories_kcal"] == 70 * 26  # calorie_factor for Beginner is 26

    def test_response_contains_expected_keys(self, client):
        res = client.get("/programs/Fat Loss (FL)/calories?weight=60")
        assert res.status_code == 200
        keys = res.get_json().keys()
        assert {"program", "description", "weight_kg", "calories_kcal", "allowed_memberships"} <= set(keys)

    def test_invalid_program_returns_404(self, client):
        res = client.get("/programs/NonExistent/calories?weight=70")
        assert res.status_code == 404

    def test_missing_weight_returns_400(self, client):
        res = client.get("/programs/Beginner (BG)/calories")
        assert res.status_code == 400

    def test_zero_weight_returns_400(self, client):
        res = client.get("/programs/Beginner (BG)/calories?weight=0")
        assert res.status_code == 400