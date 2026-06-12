"""Unit tests verifying the completed transaction user review backend mechanics."""

import pytest
from app import create_app
from app.models import db, Transaction, User


@pytest.fixture
def app():
    """Sets up an isolated test database application context environment."""
    flask_app = create_app()
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['TESTING'] = True

    with flask_app.app_context():
        db.create_all()
        
        # Safe dummy dynamic records generation to satisfy relational FKs
        u1 = User(id=1, email="test1@domain.com", display_name="User One")
        u2 = User(id=2, email="test2@domain.com", display_name="User Two")
        db.session.add_all([u1, u2])
        db.session.commit()

        dummy_tx = Transaction(id=100, listing_id=999, buyer_id=1, seller_id=2)
        db.session.add(dummy_tx)
        db.session.commit()
        
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    """Provides a functional mock HTTP application test client wrapper."""
    return app.test_client()


def test_submit_valid_review(client):
    """Verifies that clean payloads register safely with a 201 created code."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 5, "comment": "Excellent!"}
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 201


def test_submit_invalid_rating(client):
    """Verifies that out-of-bounds ratings trigger validation rejections."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 99}
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 400


def test_submit_duplicate_review(client):
    """Ensures database constraint unique parameters catch double-submissions."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 4}
    client.post('/api/reviews', json=payload)
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 409


def test_null_state_unrated_user(client):
    """Verifies unrated traders cleanly respond with empty state configurations."""
    response = client.get('/api/users/1/reviews')
    assert response.status_code == 200
    assert response.get_json()["average_rating_display"] == "No ratings yet (New Trader)"