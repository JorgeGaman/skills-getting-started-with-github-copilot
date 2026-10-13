import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory database after every test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all():
    # Arrange / Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert len(data) >= 9


def test_signup_adds_participant():
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_twice_is_rejected():
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_unknown_activity_returns_404():
    # Act
    response = client.post("/activities/Unknown/signup", params={"email": "a@b.edu"})

    # Assert
    assert response.status_code == 404


def test_unregister_removes_participant():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_signed_up_returns_400():
    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": "nobody@mergington.edu"})

    # Assert
    assert response.status_code == 400


def test_unregister_unknown_activity_returns_404():
    # Act
    response = client.delete("/activities/Unknown/unregister", params={"email": "a@b.edu"})

    # Assert
    assert response.status_code == 404
