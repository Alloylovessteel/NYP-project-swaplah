"""Tests for SwapLah offers and transactions routes."""

import pytest

from app import create_app
from app.models import db, User, Listing, Offer, Transaction


@pytest.fixture
def app():
    """Create a fresh in-memory application for each test."""
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
        "SECRET_KEY": "test-secret-key"
    })

    with test_app.app_context():
        db.drop_all()
        db.create_all()

        seller = User(
            student_id="240000A",
            first_name="Test",
            last_name="Seller",
            display_name="Seller",
            email="seller@mymail.nyp.edu.sg",
            contact_number="90000001",
            password_hash="test"
        )

        buyer = User(
            student_id="240001B",
            first_name="Test",
            last_name="Buyer",
            display_name="Buyer",
            email="buyer@mymail.nyp.edu.sg",
            contact_number="90000002",
            password_hash="test"
        )

        second_buyer = User(
            student_id="240002C",
            first_name="Second",
            last_name="Buyer",
            display_name="Buyer Two",
            email="buyer2@mymail.nyp.edu.sg",
            contact_number="90000003",
            password_hash="test"
        )

        db.session.add_all([seller, buyer, second_buyer])
        db.session.commit()

        target_listing = Listing(
            title="Mechanical Keyboard",
            description="Working keyboard in good condition",
            price="50",
            category="Electronics",
            condition="Good",
            image_url="https://example.com/keyboard.jpg",
            seller_id=seller.id
        )

        swap_listing = Listing(
            title="Gaming Mouse",
            description="Mouse offered as a swap",
            price="Swap Only",
            category="Electronics",
            condition="Like New",
            image_url="https://example.com/mouse.jpg",
            seller_id=buyer.id
        )

        db.session.add_all([target_listing, swap_listing])
        db.session.commit()

        test_app.config["SELLER_ID"] = seller.id
        test_app.config["BUYER_ID"] = buyer.id
        test_app.config["SECOND_BUYER_ID"] = second_buyer.id
        test_app.config["TARGET_LISTING_ID"] = target_listing.id
        test_app.config["SWAP_LISTING_ID"] = swap_listing.id

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return the Flask test client."""
    return app.test_client()


def login_as(client, user_id):
    """Place a user ID directly into the test session."""
    with client.session_transaction() as test_session:
        test_session["user_id"] = user_id


def test_create_price_offer_success(client, app):
    """A buyer can submit a price offer."""
    login_as(client, app.config["BUYER_ID"])

    response = client.post(
        "/api/offers",
        json={
            "listing_id": app.config["TARGET_LISTING_ID"],
            "offer_price": "45"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Offer submitted successfully"
    assert data["offer"]["offer_price"] == "45"
    assert data["offer"]["status"] == "pending"

    with app.app_context():
        offer = Offer.query.first()

        assert offer is not None
        assert offer.buyer_id == app.config["BUYER_ID"]
        assert offer.offer_price == "45"


def test_create_swap_offer_success(client, app):
    """A buyer can submit one of their listings as a swap."""
    login_as(client, app.config["BUYER_ID"])

    response = client.post(
        "/api/offers",
        json={
            "listing_id": app.config["TARGET_LISTING_ID"],
            "swap_listing_id": app.config["SWAP_LISTING_ID"]
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["offer"]["swap_listing_id"] == (
        app.config["SWAP_LISTING_ID"]
    )

    assert data["offer"]["offer_price"] is None


def test_cannot_offer_on_own_listing(client, app):
    """A seller cannot submit an offer on their own listing."""
    login_as(client, app.config["SELLER_ID"])

    response = client.post(
        "/api/offers",
        json={
            "listing_id": app.config["TARGET_LISTING_ID"],
            "offer_price": "40"
        }
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "You cannot make an offer on your own listing"
    )


def test_unauthorized_user_cannot_create_offer(client, app):
    """A logged-out user cannot submit an offer."""
    response = client.post(
        "/api/offers",
        json={
            "listing_id": app.config["TARGET_LISTING_ID"],
            "offer_price": "40"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_offer_requires_price_or_swap(client, app):
    """An offer must contain a proposed price or swap listing."""
    login_as(client, app.config["BUYER_ID"])

    response = client.post(
        "/api/offers",
        json={
            "listing_id": app.config["TARGET_LISTING_ID"]
        }
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Provide either offer_price or swap_listing_id"
    )


def test_seller_can_view_pending_offers(client, app):
    """The listing seller can view pending offers."""
    with app.app_context():
        offer = Offer(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["BUYER_ID"],
            offer_price="45",
            status="pending"
        )

        db.session.add(offer)
        db.session.commit()

    login_as(client, app.config["SELLER_ID"])

    response = client.get(
        f"/api/listings/{app.config['TARGET_LISTING_ID']}/offers"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["offers"]) == 1
    assert data["offers"][0]["offer_price"] == "45"
    assert data["offers"][0]["status"] == "pending"


def test_buyer_cannot_view_seller_pending_offers(client, app):
    """A buyer cannot view offers for another user's listing."""
    login_as(client, app.config["BUYER_ID"])

    response = client.get(
        f"/api/listings/{app.config['TARGET_LISTING_ID']}/offers"
    )

    assert response.status_code == 403

    assert response.get_json()["error"] == (
        "Only the listing seller can view its offers"
    )


def test_seller_can_reject_offer(client, app):
    """A seller can reject a pending offer."""
    with app.app_context():
        offer = Offer(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["BUYER_ID"],
            offer_price="45",
            status="pending"
        )

        db.session.add(offer)
        db.session.commit()

        offer_id = offer.id

    login_as(client, app.config["SELLER_ID"])

    response = client.post(
        f"/api/offers/{offer_id}/reject"
    )

    assert response.status_code == 200
    assert response.get_json()["offer"]["status"] == "rejected"

    with app.app_context():
        rejected_offer = db.session.get(Offer, offer_id)
        assert rejected_offer.status == "rejected"


def test_accept_offer_creates_transaction(client, app):
    """Accepting an offer creates a transaction."""
    with app.app_context():
        offer = Offer(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["BUYER_ID"],
            offer_price="45",
            status="pending"
        )

        db.session.add(offer)
        db.session.commit()

        offer_id = offer.id

    login_as(client, app.config["SELLER_ID"])

    response = client.post(
        f"/api/offers/{offer_id}/accept"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["offer"]["status"] == "accepted"
    assert data["transaction"]["buyer_id"] == (
        app.config["BUYER_ID"]
    )

    assert data["transaction"]["seller_id"] == (
        app.config["SELLER_ID"]
    )

    with app.app_context():
        transaction = Transaction.query.first()
        assert transaction is not None


def test_accepting_offer_auto_rejects_competing_offers(client, app):
    """Accepting one offer rejects other pending offers."""
    with app.app_context():
        accepted_offer = Offer(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["BUYER_ID"],
            offer_price="45",
            status="pending"
        )

        competing_offer = Offer(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["SECOND_BUYER_ID"],
            offer_price="47",
            status="pending"
        )

        db.session.add_all([
            accepted_offer,
            competing_offer
        ])

        db.session.commit()

        accepted_offer_id = accepted_offer.id
        competing_offer_id = competing_offer.id

    login_as(client, app.config["SELLER_ID"])

    response = client.post(
        f"/api/offers/{accepted_offer_id}/accept"
    )

    assert response.status_code == 200

    with app.app_context():
        accepted_offer = db.session.get(
            Offer,
            accepted_offer_id
        )

        competing_offer = db.session.get(
            Offer,
            competing_offer_id
        )

        assert accepted_offer.status == "accepted"
        assert competing_offer.status == "rejected"


def test_buyer_can_view_transaction_history(client, app):
    """A buyer can view transactions involving them."""
    with app.app_context():
        transaction = Transaction(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["BUYER_ID"],
            seller_id=app.config["SELLER_ID"]
        )

        db.session.add(transaction)
        db.session.commit()

    login_as(client, app.config["BUYER_ID"])

    response = client.get("/api/transactions")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["transactions"]) == 1

    assert data["transactions"][0]["buyer_id"] == (
        app.config["BUYER_ID"]
    )


def test_unrelated_user_does_not_see_transaction(client, app):
    """Users only see transactions involving themselves."""
    with app.app_context():
        transaction = Transaction(
            listing_id=app.config["TARGET_LISTING_ID"],
            buyer_id=app.config["BUYER_ID"],
            seller_id=app.config["SELLER_ID"]
        )

        db.session.add(transaction)
        db.session.commit()

    login_as(client, app.config["SECOND_BUYER_ID"])

    response = client.get("/api/transactions")

    assert response.status_code == 200
    assert response.get_json()["transactions"] == []