"""API tests for reviews."""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db, User, Listing, Transaction


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()

            buyer = User(
                student_id="S1000001", first_name="Bob", last_name="Buyer",
                display_name="Bob B", email="bob@nyp.edu.sg",
                contact_number="90000001",
                password_hash=generate_password_hash("Pass1234!")
            )
            seller = User(
                student_id="S1000002", first_name="Sam", last_name="Seller",
                display_name="Sam S", email="sam@nyp.edu.sg",
                contact_number="90000002",
                password_hash=generate_password_hash("Pass1234!")
            )
            stranger = User(
                student_id="S1000003", first_name="Ivy", last_name="Irrelevant",
                display_name="Ivy I", email="ivy@nyp.edu.sg",
                contact_number="90000003",
                password_hash=generate_password_hash("Pass1234!")
            )
            db.session.add_all([buyer, seller, stranger])
            db.session.commit()

            listing = Listing(
                title="Used Calculator", description="Works fine",
                price="10", category="Electronics", condition="Good",
                image_url="http://example.com/img.png", seller_id=seller.id
            )
            db.session.add(listing)
            db.session.commit()

            transaction = Transaction(
                listing_id=listing.id, buyer_id=buyer.id, seller_id=seller.id
            )
            db.session.add(transaction)
            db.session.commit()

        yield client


def login(client, email):
    return client.post("/api/login", json={
        "email": email, "password": "Pass1234!"
    })


# --- Auth guard ---

def test_create_review_requires_login(client):
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5}
    )
    assert response.status_code == 401


# --- Transaction validation ---

def test_missing_transaction_id(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"rating": 5}
    )
    assert response.status_code == 400


def test_unknown_transaction_id(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 9999, "rating": 5}
    )
    assert response.status_code == 404


def test_non_participant_cannot_review(client):
    login(client, "ivy@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5}
    )
    assert response.status_code == 403


def test_reviewee_mismatch_rejected(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "reviewee_id": 999, "rating": 5}
    )
    assert response.status_code == 400


# --- Rating / comment validation (buyer reviewing seller) ---

def test_missing_rating(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1}
    )
    assert response.status_code == 400


def test_invalid_rating(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 10}
    )
    assert response.status_code == 400


def test_comment_too_long(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5, "comment": "a" * 501}
    )
    assert response.status_code == 400


# --- Happy path + duplicate check ---

def test_buyer_can_review_seller(client):
    login(client, "bob@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5, "comment": "Great seller!"}
    )
    assert response.status_code == 201
    assert response.json["review"]["reviewee_id"] is not None


def test_duplicate_review_rejected(client):
    login(client, "bob@nyp.edu.sg")
    client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5}
    )
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 4}
    )
    assert response.status_code == 400


def test_seller_can_review_buyer(client):
    login(client, "sam@nyp.edu.sg")
    response = client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 4, "comment": "Prompt payment"}
    )
    assert response.status_code == 201


# --- Reading reviews ---

def test_no_ratings(client):
    response = client.get("/api/users/9999/reviews")
    assert response.status_code == 200
    assert response.json["review_count"] == 0
    assert response.json["reviews"] == []


def test_average_rating_after_review(client):
    login(client, "bob@nyp.edu.sg")
    client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5}
    )

    seller_reviews = client.get("/api/users/2/reviews")
    assert seller_reviews.status_code == 200
    assert seller_reviews.json["average_rating"] == 5.0
    assert seller_reviews.json["review_count"] == 1
    assert len(seller_reviews.json["reviews"]) == 1


# --- Pending reviews ---

def test_pending_reviews_requires_login(client):
    response = client.get("/api/reviews/pending")
    assert response.status_code == 401


def test_pending_reviews_lists_unreviewed_transaction(client):
    login(client, "bob@nyp.edu.sg")
    response = client.get("/api/reviews/pending")
    assert response.status_code == 200
    assert response.json["user_id"] == 1
    assert len(response.json["pending_reviews"]) == 1
    assert response.json["pending_reviews"][0]["your_role"] == "buyer"


def test_transaction_history_page_renders(client):
    login(client, "bob@nyp.edu.sg")
    response = client.get("/transaction-history")
    assert response.status_code == 200


def test_pending_reviews_empty_after_reviewing(client):
    login(client, "bob@nyp.edu.sg")
    client.post(
        "/api/reviews",
        json={"transaction_id": 1, "rating": 5}
    )
    response = client.get("/api/reviews/pending")
    assert response.status_code == 200
    assert response.json["pending_reviews"] == []