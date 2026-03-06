import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app

app = create_app()
client = app.test_client()


def test_home():
    response = client.get("/")
    assert response.status_code == 200


def test_add_member():
    response = client.post("/members", json={
        "name": "Alex",
        "age": 25,
        "membership": "Gold"
    })
    assert response.status_code == 201


def test_get_members():
    response = client.get("/members")
    assert response.status_code == 200