"""Unit tests for Administrator Authentication."""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User


@pytest.fixture
def client():
    """Create test client and temporary database."""

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            admin = User(
                student_id="240000A",
                first_name="Admin",
                last_name="User",
                display_name="Administrator",
                email="admin@nyp.edu.sg",
                contact_number="12345678",
                password_hash=generate_password_hash("admin123"),
                account_status="active",
                is_admin=True
            )

            student = User(
                student_id="240001A",
                first_name="Student",
                last_name="User",
                display_name="Student",
                email="student@mymail.nyp.edu.sg",
                contact_number="87654321",
                password_hash=generate_password_hash("student123"),
                account_status="active",
                is_admin=False
            )

            db.session.add(admin)
            db.session.add(student)
            db.session.commit()

            yield client

            db.drop_all()


# ----------------------------------------
# TC07
# Administrator logs in successfully
# ----------------------------------------

def test_admin_login_success(client):

    response = client.post("/api/admin/login", json={
        "email": "admin@nyp.edu.sg",
        "password": "admin123"
    })

    assert response.status_code == 200
    assert response.get_json()["message"] == "Administrator login successful"


# ----------------------------------------
# TC08
# Invalid administrator password
# ----------------------------------------

def test_admin_login_invalid_password(client):

    response = client.post("/api/admin/login", json={
        "email": "admin@nyp.edu.sg",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert "Invalid email or password" in response.get_json()["error"]


# ----------------------------------------
# TC09
# Student account attempts administrator login
# ----------------------------------------

def test_student_cannot_login_admin_portal(client):

    response = client.post("/api/admin/login", json={
        "email": "student@mymail.nyp.edu.sg",
        "password": "student123"
    })

    assert response.status_code == 403
    assert "not an administrator" in response.get_json()["error"]


# ----------------------------------------
# TC10
# Administrator attempts student login
# ----------------------------------------

def test_admin_cannot_login_student_portal(client):

    response = client.post("/api/login", json={
        "email": "admin@nyp.edu.sg",
        "password": "admin123"
    })

    assert response.status_code == 403
    assert "Administrator Login" in response.get_json()["error"]


# ----------------------------------------
# TC11
# Access Reports page without logging in
# ----------------------------------------

def test_reports_page_requires_admin_login(client):

    with client.session_transaction() as sess:
        sess.clear()

    response = client.get("/admin/reports")

    assert response.status_code in (302, 401, 403)


# ----------------------------------------
# TC12
# Access User Management page without logging in
# ----------------------------------------

def test_users_page_requires_admin_login(client):

    with client.session_transaction() as sess:
        sess.clear()

    response = client.get("/admin/users")

    assert response.status_code in (302, 401, 403)


# ----------------------------------------
# TC13
# Administrator logs out successfully
# ----------------------------------------

def test_admin_logout_success(client):

    client.post("/api/admin/login", json={
        "email": "admin@nyp.edu.sg",
        "password": "admin123"
    })

    response = client.get("/admin/logout")

    assert response.status_code in (200, 302)

    with client.session_transaction() as sess:
        assert "user_id" not in sess

# ----------------------------------------
# Additional Test
# Administrator login with missing email
# ----------------------------------------

def test_admin_login_missing_email(client):

    response = client.post("/api/admin/login", json={
        "password": "admin123"
    })

    assert response.status_code == 400


# ----------------------------------------
# Additional Test
# Administrator login with missing password
# ----------------------------------------

def test_admin_login_missing_password(client):

    response = client.post("/api/admin/login", json={
        "email": "admin@nyp.edu.sg"
    })

    assert response.status_code == 400


# ----------------------------------------
# Additional Test
# Non-existent administrator account
# ----------------------------------------

def test_admin_login_nonexistent_account(client):

    response = client.post("/api/admin/login", json={
        "email": "unknown@nyp.edu.sg",
        "password": "password123"
    })

    assert response.status_code == 401


# ----------------------------------------
# Additional Test
# Administrator cannot access after logout
# ----------------------------------------

def test_admin_cannot_access_after_logout(client):

    client.post("/api/admin/login", json={
        "email": "admin@nyp.edu.sg",
        "password": "admin123"
    })

    client.get("/admin/logout")

    response = client.get("/admin/reports")

    assert response.status_code in (302, 401, 403)


# ----------------------------------------
# Additional Test
# Student cannot access reports page
# ----------------------------------------

def test_student_cannot_access_reports_page(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 2

    response = client.get("/admin/reports")

    assert response.status_code == 403


# ----------------------------------------
# Additional Test
# Student cannot access user management page
# ----------------------------------------

def test_student_cannot_access_users_page(client):

    with client.session_transaction() as sess:
        sess["user_id"] = 2

    response = client.get("/admin/users")

    assert response.status_code == 403