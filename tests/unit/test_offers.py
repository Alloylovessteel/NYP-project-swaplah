import pytest

from app import create_app
from app.models import db, User, Listing, Offer, Transaction


@pytest.fixture
def client():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SECRET_KEY": "test-secret-key"
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        buyer = User(
        id=1,
        email="buyer@example.com",
        password_hash="test"
)

        seller = User(
        id=2,
        email="seller@example.com",
        password_hash="test"
)

        listing = Listing(
        title="Test Item",
        description="Test description",
        price="50",
        category="Electronics",
        condition="Good",
        seller_id=2
)

        db.session.add_all([buyer, seller, listing])
        db.session.commit()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def login_as_user(client, user_id):
    with client.session_transaction() as session:
        session["user_id"] = user_id


def test_create_offer_success(client):
    """Buyer can submit a valid offer."""
    login_as_user(client, 1)

    listing = Listing.query.first()

    response = client.post(
        "/api/offers",
        json={
            "listing_id": listing.id,
            "offer_price": 40
        }
    )

    assert response.status_code == 201
    assert Offer.query.count() == 1

    offer = Offer.query.first()
    assert offer.buyer_id == 1
    assert offer.listing_id == listing.id
    assert float(offer.offer_price) == 40
    assert offer.status == "pending"


def test_create_offer_requires_login(client):
    """Unauthenticated users cannot submit offers."""
    listing = Listing.query.first()

    response = client.post(
        "/api/offers",
        json={
            "listing_id": listing.id,
            "offer_price": 40
        }
    )

    assert response.status_code == 401
    assert Offer.query.count() == 0


def test_seller_can_accept_offer(client):
    """Seller can accept an offer."""
    listing = Listing.query.first()

    offer = Offer(
        listing_id=listing.id,
        buyer_id=1,
        offer_price=40,
        status="pending"
    )

    db.session.add(offer)
    db.session.commit()

    login_as_user(client, 2)

    response = client.post(f"/api/offers/{offer.id}/accept")

    assert response.status_code == 200

    updated_offer = db.session.get(Offer, offer.id)
    assert updated_offer.status == "accepted"
    assert Transaction.query.count() == 1


def test_seller_can_reject_offer(client):
    """Seller can reject an offer."""
    listing = Listing.query.first()

    offer = Offer(
        listing_id=listing.id,
        buyer_id=1,
        offer_price=40,
        status="pending"
    )

    db.session.add(offer)
    db.session.commit()

    login_as_user(client, 2)

    response = client.post(f"/api/offers/{offer.id}/reject")

    assert response.status_code == 200

    updated_offer = db.session.get(Offer, offer.id)
    assert updated_offer.status == "rejected"


def test_transactions_require_login(client):
    """Unauthenticated users cannot view transactions."""
    response = client.get("/api/transactions")

    assert response.status_code == 401