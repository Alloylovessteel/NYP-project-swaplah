"""Unit tests for Reporting & Administration."""

import pytest
from app import create_app, db
from app.models import User, Listing, Report


@pytest.fixture
def client():
    """Setup temporary database and test client."""

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            user = User(
                id=1,
                student_id="240000A",
                first_name="Admin",
                last_name="User",
                display_name="Admin",
                email="admin@nyp.edu.sg",
                contact_number="12345678",
                password_hash="hash",
                account_status="active"
            )

            db.session.add(user)
            db.session.commit()

            with client.session_transaction() as sess:
                sess["user_id"] = 1

            yield client

            db.drop_all()


def create_listing(client):
    """Helper function to create one listing."""

    response = client.post("/api/listings", json={
        "title": "Laptop",
        "description": "Gaming laptop",
        "price": "1000",
        "category": "Electronics",
        "condition": "Good",
        "image_url": "test.jpg"
    })

    return response.json["id"]


# -----------------------------
# TC01
# Submit Report Successfully
# -----------------------------
def test_submit_report_success(client):

    listing_id = create_listing(client)

    response = client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": "Spam",
        "description": "Fake listing"
    })

    assert response.status_code == 201


# -----------------------------
# TC02
# Missing Fields
# -----------------------------
def test_submit_report_missing_fields(client):

    listing_id = create_listing(client)

    response = client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": ""
    })

    assert response.status_code == 400


# -----------------------------
# TC03
# View Reports
# -----------------------------
def test_view_reports(client):

    listing_id = create_listing(client)

    client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": "Spam",
        "description": "Fake"
    })

    response = client.get("/api/admin/reports")

    assert response.status_code == 200
    assert len(response.json) == 1


# -----------------------------
# TC04
# Dismiss Report
# -----------------------------
def test_dismiss_report(client):

    listing_id = create_listing(client)

    client.post("/api/reports", json={
        "listing_id": listing_id,
        "reason": "Spam",
        "description": "Fake"
    })

    reports = client.get("/api/admin/reports").json

    report_id = reports[0]["id"]

    response = client.delete(f"/api/admin/reports/{report_id}")

    assert response.status_code == 200


# -----------------------------
# TC05
# View Users
# -----------------------------
def test_view_users(client):

    response = client.get("/api/admin/users")

    assert response.status_code == 200
    assert len(response.json) == 1


# -----------------------------
# TC06
# Suspend User
# -----------------------------
def test_suspend_user(client):

    response = client.put("/api/admin/users/1/suspend")

    assert response.status_code == 200

    users = client.get("/api/admin/users").json

    assert users[0]["account_status"] == "suspended"


# -----------------------------
# TC07
# Unsuspend User
# -----------------------------
def test_unsuspend_user(client):

    client.put("/api/admin/users/1/suspend")

    response = client.put("/api/admin/users/1/unsuspend")

    assert response.status_code == 200

    users = client.get("/api/admin/users").json

    assert users[0]["account_status"] == "active"