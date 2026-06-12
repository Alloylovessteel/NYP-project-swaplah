"""Unit tests for the Flask-SQLAlchemy Reviews and Ratings implementation."""

import pytest
from app import create_app
from app.models import db, Transaction


@pytest.fixture
def app():
    """Sets up an isolated in-memory testing environment using the app factory configuration."""
    flask_app = create_app()
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with flask_app.app_context():
        db.create_all()
        # Seed a baseline transaction record to pass the AC-1 gating validation checks
        dummy_tx = Transaction(id=100, listing_id="list-1", buyer_id=1, seller_id=2)
        db.session.add(dummy_tx)
        db.session.commit()
        yield flask_app
        db.drop_all()


@pytest.fixture
def client(app):
    """Provides test client framework execution wrapper."""
    return app.test_client()


def test_submit_valid_review(client):
    """Verifies valid submissions insert into SQLAlchemy tracking seamlessly."""
    payload = {
        "transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2,
        "rating": 5, "comment": "Excellent item, clean swap!"
    }
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 201


def test_submit_invalid_rating(client):
    """AC-2: Assures out-of-bounds inputs throw a 400 rejection message."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 9}
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 400


def test_submit_duplicate_review(client):
    """AC-3: Ensures unique composite blocks duplicate submissions across same transaction."""
    payload = {"transaction_id": 100, "reviewer_id": 1, "reviewee_id": 2, "rating": 4}
    client.post('/api/reviews', json=payload)
    response = client.post('/api/reviews', json=payload)
    assert response.status_code == 409


def test_null_state_unrated_user(client):
    """AC-4: Validates clean fallback text formatting returns for unrated records."""
    response = client.get('/api/users/888/reviews')
    assert response.get_json()["average_rating_display"] == "No ratings yet (New Trader)"


def test_complex_rounding_fractions(client):
    """AC-1 & AC-3: Assures complex values resolve to a clean 1-decimal place balance."""
    with client.application.app_context():
        db.session.add(Transaction(id=101, listing_id="l-2", buyer_id=1, seller_id=5))
        db.session.add(Transaction(id=102, listing_id="l-3", buyer_id=2, seller_id=5))
        db.session.add(Transaction(id=103, listing_id="l-4", buyer_id=3, seller_id=5))
        db.session.commit()

    client.post('/api/reviews', json={"transaction_id": 101, "reviewer_id": 1, "reviewee_id": 5, "rating": 4})
    client.post('/api/reviews', json={"transaction_id": 102, "reviewer_id": 2, "reviewee_id": 5, "rating": 4})
    client.post('/api/reviews', json={"transaction_id": 103, "reviewer_id": 3, "reviewee_id": 5, "rating": 5})

    response = client.get('/api/users/5/reviews')
    data = response.get_json()
    assert data["numeric_rating"] == 4.3
    assert data["average_rating_display"] == "⭐ 4.3 / 5.0"