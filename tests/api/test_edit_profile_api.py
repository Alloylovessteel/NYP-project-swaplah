"""API tests for PUT /api/profile (issue #56: Edit Profile)."""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash

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
            student_id="S6000001", first_name="Mei", last_name="Tan",
            display_name="Mei T", email="mei@nyp.edu.sg",
            contact_number="90001111",
            password_hash=generate_password_hash("OldPass123!")
        )
        db.session.add(user)
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def login(client, email="mei@nyp.edu.sg", password="OldPass123!"):
    return client.post('/api/login', json={'email': email, 'password': password})


# --- Positive: fields update correctly ---

def test_edit_profile_updates_display_name(client):
    login(client)
    resp = client.put('/api/profile', json={'display_name': 'Mei Mei'})
    assert resp.status_code == 200

    profile = client.get('/api/profile').get_json()
    assert profile['display_name'] == 'Mei Mei'


def test_edit_profile_updates_contact_number(client):
    login(client)
    resp = client.put('/api/profile', json={'contact_number': '98887777'})
    assert resp.status_code == 200

    profile = client.get('/api/profile').get_json()
    assert profile['contact_number'] == '98887777'


def test_edit_profile_partial_update_leaves_other_fields_unchanged(client):
    login(client)
    client.put('/api/profile', json={'first_name': 'Meiling'})

    profile = client.get('/api/profile').get_json()
    assert profile['first_name'] == 'Meiling'
    assert profile['last_name'] == 'Tan'  # unchanged


def test_edit_profile_updates_password(client):
    login(client)
    client.put('/api/profile', json={'password': 'NewPass456!', 'current_password': 'Password123!'})

    with client.application.app_context():
        user = User.query.filter_by(email='mei@nyp.edu.sg').first()
        assert check_password_hash(user.password_hash, 'NewPass456!')
        assert not check_password_hash(user.password_hash, 'OldPass123!')


# --- Business rule: email and student ID must NOT be editable ---

def test_edit_profile_ignores_email_field(client):
    login(client)
    client.put('/api/profile', json={'email': 'hacked@nyp.edu.sg'})

    profile = client.get('/api/profile').get_json()
    assert profile['email'] == 'mei@nyp.edu.sg'  # unchanged


def test_edit_profile_ignores_student_id_field(client):
    login(client)
    client.put('/api/profile', json={'student_id': 'S9999999'})

    profile = client.get('/api/profile').get_json()
    assert profile['student_id'] == 'S6000001'  # unchanged


# --- Negative ---

def test_edit_profile_rejects_when_not_logged_in(client):
    resp = client.put('/api/profile', json={'display_name': 'Nope'})
    assert resp.status_code == 401
