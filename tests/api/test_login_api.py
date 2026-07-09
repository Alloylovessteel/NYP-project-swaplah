"""API tests for POST /api/login and POST /api/logout (issue #51)."""
import pytest

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash


@pytest.fixture
def client():
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
    }
    app = create_app(test_config)
    with app.app_context():
        user = User(
            student_id="S4000001", first_name="Amy", last_name="Lee",
            display_name="Amy L", email="amy@nyp.edu.sg",
            contact_number="98765432",
            password_hash=generate_password_hash("Pass1234!")
        )
        suspended_user = User(
            student_id="S4000002", first_name="Sus", last_name="Pended",
            display_name="Sus P", email="suspended@nyp.edu.sg",
            contact_number="98765433",
            password_hash=generate_password_hash("Pass1234!"),
            account_status="suspended"
        )
        db.session.add_all([user, suspended_user])
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


# --- Login: positive ---

def test_login_success_returns_200(client):
    resp = client.post('/api/login', json={
        'email': 'amy@nyp.edu.sg', 'password': 'Pass1234!'
    })
    assert resp.status_code == 200
    assert 'user_id' in resp.get_json()


# --- Login: negative ---

def test_login_rejects_wrong_password(client):
    resp = client.post('/api/login', json={
        'email': 'amy@nyp.edu.sg', 'password': 'WrongPass'
    })
    assert resp.status_code == 401


def test_login_rejects_nonexistent_email(client):
    resp = client.post('/api/login', json={
        'email': 'nobody@nyp.edu.sg', 'password': 'Pass1234!'
    })
    assert resp.status_code == 401


def test_login_rejects_missing_password(client):
    resp = client.post('/api/login', json={'email': 'amy@nyp.edu.sg'})
    assert resp.status_code == 400


def test_login_rejects_suspended_account(client):
    resp = client.post('/api/login', json={
        'email': 'suspended@nyp.edu.sg', 'password': 'Pass1234!'
    })
    assert resp.status_code == 403


# --- Logout ---

def test_logout_clears_session(client):
    client.post('/api/login', json={
        'email': 'amy@nyp.edu.sg', 'password': 'Pass1234!'
    })
    # confirm logged in
    profile_resp = client.get('/api/profile')
    assert profile_resp.status_code == 200

    logout_resp = client.post('/api/logout')
    assert logout_resp.status_code == 200

    # session should now be cleared - profile access denied
    profile_after_logout = client.get('/api/profile')
    assert profile_after_logout.status_code == 401


def test_logout_without_login_still_succeeds(client):
    resp = client.post('/api/logout')
    assert resp.status_code == 200
