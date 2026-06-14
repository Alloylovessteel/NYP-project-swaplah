"""API tests for reviews."""

import pytest

from app import create_app
from app.models import db


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

        yield client


def test_missing_rating(client):
    response = client.post(
        "/api/reviews",
        json={
            "transaction_id": 1,
            "reviewer_id": 1,
            "reviewee_id": 2
        }
    )

    assert response.status_code == 400


def test_invalid_rating(client):
    response = client.post(
        "/api/reviews",
        json={
            "transaction_id": 1,
            "reviewer_id": 1,
            "reviewee_id": 2,
            "rating": 10
        }
    )

    assert response.status_code == 400


def test_comment_too_long(client):
    response = client.post(
        "/api/reviews",
        json={
            "transaction_id": 1,
            "reviewer_id": 1,
            "reviewee_id": 2,
            "rating": 5,
            "comment": "a" * 501
        }
    )

    assert response.status_code == 400


def test_no_ratings(client):
    response = client.get(
        "/api/users/1/reviews"
    )

    assert response.status_code == 200
    assert response.json["review_count"] == 0