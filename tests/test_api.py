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
    VALID = {"name": "Arjun", "age": 25,"membership": "VIP"}

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
        second = {"name": "Priya", "age": 22, "membership": "Premium"}
        res = client.post("/members", json=second)
        assert res.get_json()["id"] == 2

    def test_add_member_missing_name_returns_400(self, client):
        res = client.post("/members", json={"age": 25, "membership": "Basic"})
        assert res.status_code == 400

    def test_add_member_missing_age_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "membership": "VIP"})
        assert res.status_code == 400

    def test_add_member_invalid_membership_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "age": 20, "membership": "Unknown"})
        assert res.status_code == 400

    def test_add_member_negative_age_returns_400(self, client):
        res = client.post("/members", json={"name": "X", "age": -5, "membership": "VIP"})
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
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Basic"})
        res = client.get("/members")
        assert len(res.get_json()) == 1

    def test_get_members_multiple(self, client):
        for i in range(3):
            client.post("/members", json={"name": f"User{i}", "age": 20 + i, "membership": "VIP"})
        res = client.get("/members")
        assert len(res.get_json()) == 3


# ── Get Single Member ────────────────────────────────────────────────────
class TestGetMember:
    def test_get_existing_member(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Premium"})
        res = client.get("/members/1")
        assert res.status_code == 200
        assert res.get_json()["name"] == "Arjun"

    def test_get_nonexistent_member_returns_404(self, client):
        res = client.get("/members/999")
        assert res.status_code == 404


# ── Update Member ────────────────────────────────────────────────────────
class TestUpdateMember:
    def test_update_member_age(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "VIP"})
        res = client.put("/members/1", json={"age": 30})
        assert res.status_code == 200
        assert res.get_json()["age"] == 30

    def test_update_nonexistent_member_returns_404(self, client):
        res = client.put("/members/999", json={"age": 30})
        assert res.status_code == 404


# ── Delete Member ────────────────────────────────────────────────────────
class TestDeleteMember:
    def test_delete_member_returns_200(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Basic"})
        res = client.delete("/members/1")
        assert res.status_code == 200

    def test_delete_removes_member(self, client):
        client.post("/members", json={"name": "Arjun", "age": 25, "membership": "Premium"})
        client.delete("/members/1")
        res = client.get("/members")
        assert res.get_json() == []

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/members/999")
        assert res.status_code == 404
