"""Tests for Session Timeout and Access Control (issue #52).

Verifies the 30-minute inactivity timeout is actually configured AND
enforced (session marked permanent), and that logged-out users cannot
reach protected routes.
"""
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
            student_id="S7000001", first_name="Wei", last_name="Chua",
            display_name="Wei C", email="wei@nyp.edu.sg",
            contact_number="91110000",
            password_hash=generate_password_hash("Pass1234!")
        )
        db.session.add(user)
        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_session_lifetime_configured_to_30_minutes(client):
    """PERMANENT_SESSION_LIFETIME must be 1800 seconds (30 minutes)."""
    lifetime = client.application.config['PERMANENT_SESSION_LIFETIME']
    seconds = lifetime.total_seconds() if hasattr(lifetime, 'total_seconds') else lifetime
    assert seconds == 1800


def test_login_marks_session_as_permanent(client):
    """Without session.permanent = True, the 30-min config has no effect."""
    client.post('/api/login', json={
        'email': 'wei@nyp.edu.sg', 'password': 'Pass1234!'
    })
    with client.session_transaction() as sess:
        assert sess.permanent is True


def test_protected_route_blocked_without_session(client):
    """Simulates a logged-out (or expired) user hitting a protected route."""
    resp = client.get('/api/profile')
    assert resp.status_code == 401


def test_protected_route_blocked_after_explicit_logout(client):
    client.post('/api/login', json={
        'email': 'wei@nyp.edu.sg', 'password': 'Pass1234!'
    })
    client.post('/api/logout')
    resp = client.get('/api/profile')
    assert resp.status_code == 401


def test_edit_profile_also_blocked_without_session(client):
    resp = client.put('/api/profile', json={'display_name': 'x'})
    assert resp.status_code == 401
