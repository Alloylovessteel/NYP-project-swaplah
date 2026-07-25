"""API tests for Reporting & Administration."""

import pytest

from app import create_app
from app.models import db, User, Listing, Report


@pytest.fixture
def client():
    test_config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
    }

    app = create_app(test_config)

    with app.app_context():
        admin = User(
            id=1,
            student_id="S4000001",
            first_name="Admin",
            last_name="User",
            display_name="Admin",
            email="admin@nyp.edu.sg",
            contact_number="98765432",
            password_hash="hash",
            is_admin=True
        )

        student = User(
            id=2,
            student_id="S4000002",
            first_name="John",
            last_name="Student",
            display_name="John",
            email="john@nyp.edu.sg",
            contact_number="91234567",
            password_hash="hash",
            is_admin=False
        )

        db.session.add_all([admin, student])
        db.session.commit()

    with app.test_client() as test_client:

        with test_client.session_transaction() as sess:
            sess["user_id"] = 1

        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def create_listing(client):
    response = client.post("/api/listings", json={
        "title": "Laptop",
        "description": "Gaming laptop",
        "price": "1000",
        "category": "Electronics",
        "condition": "Good",
        "image_url": "test.jpg"
    })

    return response.get_json()["id"]


# ---------- Submit Report ----------

def test_submit_report_success(client):

    listing_id = create_listing(client)

    response = client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": "Spam",
        "description": "Fake listing"
    })

    assert response.status_code == 201


def test_submit_report_missing_fields(client):

    listing_id = create_listing(client)

    response = client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": ""
    })

    assert response.status_code == 400


# ---------- View Reports ----------

def test_view_reports(client):

    listing_id = create_listing(client)

    client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": "Spam",
        "description": "Fake"
    })

    response = client.get("/api/admin/reports")

    assert response.status_code == 200
    assert len(response.get_json()) == 1


# ---------- Dismiss Report ----------

def test_dismiss_report(client):

    listing_id = create_listing(client)

    client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": "Spam",
        "description": "Fake"
    })

    reports = client.get("/api/admin/reports").get_json()

    report_id = reports[0]["id"]

    response = client.delete(f"/api/admin/reports/{report_id}")

    assert response.status_code == 200


# ---------- View Users ----------

def test_view_users(client):

    response = client.get("/api/admin/users")

    assert response.status_code == 200
    users = response.get_json()

    assert len(users) == 1
    assert users[0]["is_admin"] is False


# ---------- Suspend ----------

def test_suspend_user(client):

    response = client.put("/api/admin/users/2/suspend")

    assert response.status_code == 200


# ---------- Unsuspend ----------

def test_unsuspend_user(client):

    client.put("/api/admin/users/2/suspend")

    response = client.put("/api/admin/users/2/unsuspend")
    assert response.status_code == 200