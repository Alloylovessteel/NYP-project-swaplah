import pytest

from app import create_app
from app.models import db, User, Listing, Offer, Transaction


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key",
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        buyer = User(
            id=1,
            student_id="251891J",
            first_name="Buyer",
            last_name="Test",
            display_name="buyer",
            email="buyer@example.com",
            contact_number="91234567",
            password_hash="test",
            account_status="active",
        )

        seller = User(
            id=2,
            student_id="251892J",
            first_name="Seller",
            last_name="Test",
            display_name="seller",
            email="seller@example.com",
            contact_number="98765432",
            password_hash="test",
            account_status="active",
        )

        listing = Listing(
            title="Test Item",
            description="Test description",
            price="50",
            category="Electronics",
            condition="Good",
            image_url="https://example.com/test-item.jpg",
            seller_id=2,
        )

        db.session.add_all([buyer, seller, listing])
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def login_as_user(client, user_id):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_create_offer_api_success(client):
    """API returns 201 when a buyer submits a valid offer."""
    login_as_user(client, 1)
    listing = Listing.query.first()

    response = client.post(
        "/api/offers",
        json={
            "listing_id": listing.id,
            "offer_price": 40,
        },
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data is not None
    assert Offer.query.count() == 1

    offer = Offer.query.first()
    assert offer.buyer_id == 1
    assert offer.listing_id == listing.id
    assert float(offer.offer_price) == 40
    assert offer.status == "pending"


def test_create_offer_api_requires_login(client):
    """API returns 401 when an unauthenticated user submits an offer."""
    listing = Listing.query.first()

    response = client.post(
        "/api/offers",
        json={
            "listing_id": listing.id,
            "offer_price": 40,
        },
    )

    assert response.status_code == 401
    assert Offer.query.count() == 0


def test_accept_offer_api_success(client):
    """API allows the listing seller to accept a pending offer."""
    listing = Listing.query.first()

    offer = Offer(
        listing_id=listing.id,
        buyer_id=1,
        offer_price=40,
        status="pending",
    )

    db.session.add(offer)
    db.session.commit()

    login_as_user(client, 2)

    response = client.post(f"/api/offers/{offer.id}/accept")
    data = response.get_json()

    assert response.status_code == 200
    assert data is not None

    updated_offer = db.session.get(Offer, offer.id)
    assert updated_offer.status == "accepted"
    assert Transaction.query.count() == 1


def test_reject_offer_api_success(client):
    """API allows the listing seller to reject a pending offer."""
    listing = Listing.query.first()

    offer = Offer(
        listing_id=listing.id,
        buyer_id=1,
        offer_price=40,
        status="pending",
    )

    db.session.add(offer)
    db.session.commit()

    login_as_user(client, 2)

    response = client.post(f"/api/offers/{offer.id}/reject")

    assert response.status_code == 200

    updated_offer = db.session.get(Offer, offer.id)
    assert updated_offer.status == "rejected"


def test_reject_nonexistent_offer_api(client):
    """API returns 404 when the requested offer does not exist."""
    login_as_user(client, 2)

    response = client.post("/api/offers/99999/reject")

    assert response.status_code == 404


def test_transactions_api_requires_login(client):
    """API returns 401 when an unauthenticated user views transactions."""
    response = client.get("/api/transactions")

    assert response.status_code == 401