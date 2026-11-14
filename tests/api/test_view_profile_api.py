"""API tests for GET /api/profile (issue #54: View Profile)."""
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db, User


@pytest.fixture
def client():
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
    }
    app = create_app(test_config)
    with app.app_context():
        user = User(
            student_id="S5000001", first_name="Ken", last_name="Goh",
            display_name="Ken G", email="ken@nyp.edu.sg",
            contact_number="91231234",
            password_hash=generate_password_hash("Pass1234!")
        )
        db.session.add(user)
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def login(client, email="ken@nyp.edu.sg", password="Pass1234!"):
    return client.post('/api/login', json={'email': email, 'password': password})


# --- Positive ---

def test_view_profile_returns_correct_fields_when_logged_in(client):
    login(client)
    resp = client.get('/api/profile')
    assert resp.status_code == 200
    body = resp.get_json()
    assert body['student_id'] == 'S5000001'
    assert body['first_name'] == 'Ken'
    assert body['display_name'] == 'Ken G'
    assert body['email'] == 'ken@nyp.edu.sg'
    assert body['contact_number'] == '91231234'


def test_view_profile_does_not_leak_password_hash(client):
    login(client)
    resp = client.get('/api/profile')
    assert 'password_hash' not in resp.get_json()
    assert 'password' not in resp.get_json()


# --- Negative ---

def test_view_profile_rejects_when_not_logged_in(client):
    resp = client.get('/api/profile')
    assert resp.status_code == 401


def test_view_profile_rejects_after_logout(client):
    login(client)
    client.post('/api/logout')
    resp = client.get('/api/profile')
    assert resp.status_code == 401
