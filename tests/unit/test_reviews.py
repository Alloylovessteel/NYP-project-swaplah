"""Unit tests verifying the completed transaction user review backend mechanics."""

import pytest
from app import create_app
from app.models import db, Transaction, User


@pytest.fixture
def app():
    """Sets up an isolated database testing context matching your team app factory layout."""
    flask_app = create_app()
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['TESTING'] = True

    with flask_app.app_context():
        db.create_all()
        # Seed users and a mock transaction to fulfill validation criteria
        u1 = User(student_id="S12", first_name="A", last_name="B", display_name="A", email="a@e.com", contact_number="1", password_hash="p")
        u2 = User(student_id="S13", first_name="C", last_name="D", display_name="C", email="c@e.com", contact_number="2", password_hash="p")
        db.session.add_all([u1, u2])
        db.session.commit()

        dummy_tx = Transaction(id=100, listing_id="list-uuid", buyer_id=u1.id, seller_id=u2.id)
        db.session.add(dummy_tx)
        db.session.commit()
        
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    """Provides an active HTTP client application client context."""
    return app.test_client()


def test_submit_valid_review(client):
    """Verifies that flawless submission datasets register successfully with a 201 code."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 5, "comment": "Good trade!"}
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 201


def test_submit_invalid_rating(client):
    """AC-2: Out of bound integer rating evaluation parameters yield a 400 validation error."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 99}
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 400


def test_submit_duplicate_review(client):
    """AC-3: Ensures the unique database rule throws a 409 exception upon double submission."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 4}
    client.post('/api/reviews', json=payload)
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 409


def test_null_state_unrated_user(client):
    """AC-4: New trader profile requests provide the exact required empty state indicator string."""
    response = client.get('/api/users/1/reviews')
    assert response.status_code == 200
    assert response.get_json()["average_rating_display"] == "No ratings yet (New Trader)"