"""Unit tests for auth routes - forgot password, reset password, profile, page routes."""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app
from app.models import db, User


@pytest.fixture
def app():
    """Create test Flask app with in-memory database."""
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
    }
    flask_app = create_app(test_config)
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client with a registered user."""
    with app.app_context():
        user = User(
            student_id="S9000001", first_name="Test", last_name="User",
            display_name="Test U", email="test@nyp.edu.sg",
            contact_number="91234567",
            password_hash=generate_password_hash("TestPass123!")
        )
        db.session.add(user)
        db.session.commit()
    return app.test_client()


def login(client):
    """Helper to log in the test user."""
    return client.post('/api/login', json={
        'email': 'test@nyp.edu.sg',
        'password': 'TestPass123!'
    })


# --- Login route tests ---

def test_login_success(client):
    """Test successful login returns 200."""
    res = client.post('/api/login', json={
        'email': 'test@nyp.edu.sg',
        'password': 'TestPass123!'
    })
    assert res.status_code == 200
    assert res.get_json()['message'] == 'Login successful'


def test_login_wrong_password(client):
    """Test login with wrong password returns 401."""
    res = client.post('/api/login', json={
        'email': 'test@nyp.edu.sg',
        'password': 'WrongPass!'
    })
    assert res.status_code == 401


def test_login_missing_fields(client):
    """Test login with missing fields returns 400."""
    res = client.post('/api/login', json={'email': 'test@nyp.edu.sg'})
    assert res.status_code == 400


def test_login_suspended_user(app):
    """Test suspended user cannot login."""
    with app.app_context():
        user = User(
            student_id="S9000002", first_name="Sus", last_name="User",
            display_name="Sus U", email="sus@nyp.edu.sg",
            contact_number="98765432",
            password_hash=generate_password_hash("TestPass123!"),
            account_status="suspended"
        )
        db.session.add(user)
        db.session.commit()
    with app.test_client() as c:
        res = c.post('/api/login', json={
            'email': 'sus@nyp.edu.sg',
            'password': 'TestPass123!'
        })
        assert res.status_code == 403


# --- Logout route tests ---

def test_logout_success(client):
    """Test logout clears session."""
    login(client)
    res = client.post('/api/logout')
    assert res.status_code == 200
    assert res.get_json()['message'] == 'Logged out successfully'


# --- Profile view tests ---

def test_view_profile_when_logged_in(client):
    """Test viewing profile when logged in returns user data."""
    login(client)
    res = client.get('/api/profile')
    assert res.status_code == 200
    data = res.get_json()
    assert data['email'] == 'test@nyp.edu.sg'
    assert data['student_id'] == 'S9000001'


def test_view_profile_when_not_logged_in(client):
    """Test viewing profile without login returns 401."""
    res = client.get('/api/profile')
    assert res.status_code == 401


# --- Profile edit tests ---

def test_edit_profile_updates_display_name(client):
    """Test editing display name updates successfully."""
    login(client)
    res = client.put('/api/profile', json={'display_name': 'New Name'})
    assert res.status_code == 200
    profile = client.get('/api/profile').get_json()
    assert profile['display_name'] == 'New Name'


def test_edit_profile_requires_current_password_to_change_password(client):
    """Test changing password without current password returns 400."""
    login(client)
    res = client.put('/api/profile', json={'password': 'NewPass123!'})
    assert res.status_code == 400


def test_edit_profile_wrong_current_password(client):
    """Test changing password with wrong current password returns 400."""
    login(client)
    res = client.put('/api/profile', json={
        'password': 'NewPass123!',
        'current_password': 'WrongPass!'
    })
    assert res.status_code == 400


def test_edit_profile_not_logged_in(client):
    """Test editing profile without login returns 401."""
    res = client.put('/api/profile', json={'display_name': 'Nope'})
    assert res.status_code == 401


def test_edit_profile_cannot_change_email(client):
    """Test that email cannot be changed via edit profile."""
    login(client)
    client.put('/api/profile', json={'email': 'hacked@nyp.edu.sg'})
    profile = client.get('/api/profile').get_json()
    assert profile['email'] == 'test@nyp.edu.sg'


# --- Forgot password tests ---

def test_forgot_password_valid_email(client):
    """Test forgot password with valid email returns token."""
    res = client.post('/api/forgot-password', json={
        'email': 'test@nyp.edu.sg'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert 'token' in data


def test_forgot_password_invalid_email(client):
    """Test forgot password with unregistered email returns 404."""
    res = client.post('/api/forgot-password', json={
        'email': 'nobody@nyp.edu.sg'
    })
    assert res.status_code == 404


def test_forgot_password_missing_email(client):
    """Test forgot password with missing email returns 400."""
    res = client.post('/api/forgot-password', json={})
    assert res.status_code == 400


# --- Reset password tests ---

def test_reset_password_valid_token(client):
    """Test reset password with valid token succeeds."""
    token_res = client.post('/api/forgot-password', json={
        'email': 'test@nyp.edu.sg'
    })
    token = token_res.get_json()['token']

    res = client.post('/api/reset-password', json={
        'token': token,
        'password': 'NewPass456!'
    })
    assert res.status_code == 200
    assert res.get_json()['message'] == 'Password reset successful'


def test_reset_password_invalid_token(client):
    """Test reset password with invalid token returns 400."""
    res = client.post('/api/reset-password', json={
        'token': 'invalidtoken',
        'password': 'NewPass456!'
    })
    assert res.status_code == 400


def test_reset_password_missing_fields(client):
    """Test reset password with missing fields returns 400."""
    res = client.post('/api/reset-password', json={'token': 'sometoken'})
    assert res.status_code == 400


def test_reset_password_actually_changes_password(app, client):
    """Test that password is actually updated in database after reset."""
    token_res = client.post('/api/forgot-password', json={
        'email': 'test@nyp.edu.sg'
    })
    token = token_res.get_json()['token']
    client.post('/api/reset-password', json={
        'token': token,
        'password': 'BrandNew789!'
    })
    with app.app_context():
        user = User.query.filter_by(email='test@nyp.edu.sg').first()
        assert check_password_hash(user.password_hash, 'BrandNew789!')
        assert not check_password_hash(user.password_hash, 'TestPass123!')


# --- Page route tests ---

def test_login_page_renders(client):
    """Test login page returns 200."""
    res = client.get('/login')
    assert res.status_code == 200


def test_register_page_renders(client):
    """Test register page returns 200."""
    res = client.get('/register')
    assert res.status_code == 200


def test_profile_page_renders(client):
    """Test profile page returns 200 when logged in."""
    login(client)
    res = client.get('/profile')
    assert res.status_code == 200


def test_forgot_password_page_renders(client):
    """Test forgot password page returns 200."""
    res = client.get('/forgot-password')
    assert res.status_code == 200


def test_reset_password_page_renders(client):
    """Test reset password page returns 200."""
    res = client.get('/reset-password')
    assert res.status_code == 200


# --- Admin users route ---

