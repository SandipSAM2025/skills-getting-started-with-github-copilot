from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client():
    original_activities = deepcopy(app_module.activities)
    try:
        with TestClient(app_module.app) as test_client:
            yield test_client
    finally:
        app_module.activities.clear()
        app_module.activities.update(original_activities)


def test_root_redirects_to_static_index(client):
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activity_data(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == app_module.activities


def test_signup_adds_normalized_email(client):
    # Arrange
    activity_name = "Chess Club"
    email = "  STUDENT@EXAMPLE.COM "

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@example.com for Chess Club"
    }
    assert "student@example.com" in app_module.activities[activity_name]["participants"]


def test_signup_rejects_unknown_activity(client):
    # Arrange

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_email_case_insensitively(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": " MICHAEL@MERGINGTON.EDU "},
    )

    # Assert
    assert response.status_code == 409
    assert response.json() == {
        "detail": "Student already registered for activity"
    }


def test_signup_rejects_full_activity(client):
    # Arrange
    activity_name = "Chess Club"
    activity = app_module.activities[activity_name]
    activity["max_participants"] = len(activity["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_remove_participant_removes_normalized_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.request(
        "DELETE",
        f"/activities/{activity_name}/participants",
        params={"email": " MICHAEL@MERGINGTON.EDU "},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered michael@mergington.edu from Chess Club"
    }
    assert "michael@mergington.edu" not in app_module.activities[activity_name][
        "participants"
    ]


def test_remove_participant_rejects_unknown_activity(client):
    # Arrange

    # Act
    response = client.request(
        "DELETE",
        "/activities/Unknown Club/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_missing_participant(client):
    # Arrange

    # Act
    response = client.request(
        "DELETE",
        "/activities/Chess Club/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
