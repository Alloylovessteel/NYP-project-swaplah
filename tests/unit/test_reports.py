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

            admin = User(
                id=1,
                student_id="240000A",
                first_name="Admin",
                last_name="User",
                display_name="Admin",
                email="admin@nyp.edu.sg",
                contact_number="12345678",
                password_hash="hash",
                account_status="active",
                is_admin=True
            )

            student = User(
                id=2,
                student_id="240001A",
                first_name="John",
                last_name="Student",
                display_name="John",
                email="john@nyp.edu.sg",
                contact_number="87654321",
                password_hash="hash",
                account_status="active",
                is_admin=False
            )

            db.session.add_all([admin, student])
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
# View Users
# -----------------------------
def test_view_users(client):

    response = client.get("/api/admin/users")

    assert response.status_code == 200

    users = response.json

    assert len(users) == 1
    assert users[0]["display_name"] == "John"
    assert users[0]["is_admin"] is False


# -----------------------------
# TC05
# Suspend User
# -----------------------------
def test_suspend_user(client):

    response = client.put("/api/admin/users/2/suspend")

    assert response.status_code == 200

    users = client.get("/api/admin/users").json

    student = next(user for user in users if user["id"] == 2)

    assert student["account_status"] == "suspended"


# -----------------------------
# TC06
# Unsuspend User
# -----------------------------
def test_unsuspend_user(client):

    client.put("/api/admin/users/2/suspend")

    response = client.put("/api/admin/users/2/unsuspend")

    assert response.status_code == 200

    users = client.get("/api/admin/users").json

    student = next(user for user in users if user["id"] == 2)

    assert student["account_status"] == "active"

# -----------------------------
# Additional Test
# Submit Report for Non-existent Listing
# -----------------------------
def test_submit_report_invalid_listing(client):

    response = client.post("/api/reports", json={
        "listing_id": "invalid-listing-id",
        "reason": "Spam",
        "description": "Fake listing"
    })

    assert response.status_code == 404


# -----------------------------
# Additional Test
# View Reports When Empty
# -----------------------------
def test_view_reports_empty(client):

    response = client.get("/api/admin/reports")

    assert response.status_code == 200
    assert response.json == []


# -----------------------------
# Additional Test
# Suspend Non-existent User
# -----------------------------
def test_suspend_invalid_user(client):

    response = client.put("/api/admin/users/999/suspend")

    assert response.status_code == 404


# -----------------------------
# Additional Test
# Unsuspend Non-existent User
# -----------------------------
def test_unsuspend_invalid_user(client):

    response = client.put("/api/admin/users/999/unsuspend")

    assert response.status_code == 404


# -----------------------------
# Additional Test
# Non-admin Cannot View Users
# -----------------------------
def test_non_admin_cannot_view_users(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 2

    response = client.get("/api/admin/users")

    assert response.status_code == 403


# -----------------------------
# Additional Test
# Non-admin Cannot Suspend User
# -----------------------------
def test_non_admin_cannot_suspend_user(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 2

    response = client.put("/api/admin/users/2/suspend")

    assert response.status_code == 403