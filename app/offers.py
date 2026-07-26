from flask import Blueprint, jsonify, request, session
from datetime import datetime, timezone
from app.models import db, Listing, Offer, Transaction


offers_bp = Blueprint("offers", __name__)


def get_logged_in_user_id():
    """Return the logged-in user's ID from the Flask session."""
    return session.get("user_id")


@offers_bp.route("/api/offers", methods=["POST"])
def create_offer():
    """Create a price offer, swap offer, or both for a listing."""

    buyer_id = get_logged_in_user_id()

    if not buyer_id:
        return jsonify({"error": "You must be logged in"}), 401

    data = request.get_json(silent=True) or {}

    listing_id = data.get("listing_id")
    offer_price = data.get("offer_price")
    swap_listing_id = data.get("swap_listing_id")

    if not listing_id:
        return jsonify({"error": "listing_id is required"}), 400

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    if listing.seller_id == buyer_id:
        return jsonify(
            {"error": "You cannot make an offer on your own listing"}
        ), 400

    if offer_price is None and not swap_listing_id:
        return jsonify(
            {"error": "Provide an offer price or a swap listing"}
        ), 400

    if offer_price is not None:
        try:
            offer_price = float(offer_price)
        except (TypeError, ValueError):
            return jsonify(
                {"error": "offer_price must be a valid number"}
            ), 400

        if offer_price <= 0:
            return jsonify(
                {"error": "offer_price must be greater than 0"}
            ), 400

    if swap_listing_id:
        swap_listing = Listing.query.get(swap_listing_id)

        if not swap_listing:
            return jsonify({"error": "Swap listing not found"}), 404

        if swap_listing.seller_id != buyer_id:
            return jsonify(
                {"error": "You can only offer one of your own listings"}
            ), 403

        if swap_listing.id == listing.id:
            return jsonify(
                {"error": "A listing cannot be swapped for itself"}
            ), 400

    existing_offer = Offer.query.filter_by(
        listing_id=listing_id,
        buyer_id=buyer_id,
        status="pending",
    ).first()

    if existing_offer:
        return jsonify(
            {"error": "You already have a pending offer for this listing"}
        ), 409

    offer = Offer(
        listing_id=listing_id,
        buyer_id=buyer_id,
        offer_price=offer_price,
        swap_listing_id=swap_listing_id,
        status="pending",
    )

    try:
        db.session.add(offer)
        db.session.commit()

        return jsonify(
            {
                "message": "Offer created successfully",
                "offer": serialize_offer(offer),
            }
        ), 201

    except Exception:
        db.session.rollback()

        return jsonify(
            {"error": "Unable to create offer"}
        ), 500


@offers_bp.route(
    "/api/listings/<string:listing_id>/offers",
    methods=["GET"],
)
def get_listing_offers(listing_id):
    """Return all offers for a listing owned by the logged-in seller."""

    seller_id = get_logged_in_user_id()

    if not seller_id:
        return jsonify({"error": "You must be logged in"}), 401

    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    if listing.seller_id != seller_id:
        return jsonify(
            {"error": "Only the listing owner can view these offers"}
        ), 403

    offers = (
        Offer.query
        .filter_by(listing_id=listing_id)
        .order_by(Offer.created_at.desc())
        .all()
    )

    return jsonify(
        {
            "listing_id": listing_id,
            "offers": [serialize_offer(offer) for offer in offers],
        }
    ), 200


@offers_bp.route(
    "/api/offers/<int:offer_id>/accept",
    methods=["POST"],
)
def accept_offer(offer_id):
    """Accept an offer and automatically reject competing offers."""

    seller_id = get_logged_in_user_id()

    if not seller_id:
        return jsonify({"error": "You must be logged in"}), 401

    offer = Offer.query.get(offer_id)

    if not offer:
        return jsonify({"error": "Offer not found"}), 404

    listing = Listing.query.get(offer.listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    if listing.seller_id != seller_id:
        return jsonify(
            {"error": "Only the listing owner can accept this offer"}
        ), 403

    if offer.status != "pending":
        return jsonify(
            {"error": "Only pending offers can be accepted"}
        ), 400

    existing_transaction = Transaction.query.filter_by(
        listing_id=listing.id
    ).first()

    if existing_transaction:
        return jsonify(
            {"error": "A transaction already exists for this listing"}
        ), 409

    try:
        offer.status = "accepted"

        competing_offers = Offer.query.filter(
            Offer.listing_id == listing.id,
            Offer.id != offer.id,
            Offer.status == "pending",
        ).all()

        for competing_offer in competing_offers:
            competing_offer.status = "rejected"

        transaction = Transaction(
            listing_id=listing.id,
            buyer_id=offer.buyer_id,
            seller_id=listing.seller_id,
            completed_at=datetime.now(timezone.utc),
        )

        db.session.add(transaction)
        db.session.commit()

        return jsonify(
            {
                "message": "Offer accepted successfully",
                "offer": serialize_offer(offer),
                "transaction": serialize_transaction(transaction),
            }
        ), 200

    except Exception:
        db.session.rollback()

        return jsonify(
            {"error": "Unable to accept offer"}
        ), 500


@offers_bp.route(
    "/api/offers/<int:offer_id>/reject",
    methods=["POST"],
)
def reject_offer(offer_id):
    """Reject a pending offer."""

    seller_id = get_logged_in_user_id()

    if not seller_id:
        return jsonify({"error": "You must be logged in"}), 401

    offer = Offer.query.get(offer_id)

    if not offer:
        return jsonify({"error": "Offer not found"}), 404

    listing = Listing.query.get(offer.listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    if listing.seller_id != seller_id:
        return jsonify(
            {"error": "Only the listing owner can reject this offer"}
        ), 403

    if offer.status != "pending":
        return jsonify(
            {"error": "Only pending offers can be rejected"}
        ), 400

    try:
        offer.status = "rejected"
        db.session.commit()

        return jsonify(
            {
                "message": "Offer rejected successfully",
                "offer": serialize_offer(offer),
            }
        ), 200

    except Exception:
        db.session.rollback()

        return jsonify(
            {"error": "Unable to reject offer"}
        ), 500


@offers_bp.route("/api/transactions", methods=["GET"])
def get_transactions():
    """Return transactions involving the logged-in user."""

    user_id = get_logged_in_user_id()

    if not user_id:
        return jsonify({"error": "You must be logged in"}), 401

    transactions = (
        Transaction.query
        .filter(
            (Transaction.buyer_id == user_id)
            | (Transaction.seller_id == user_id)
        )
        .order_by(Transaction.completed_at.desc())
        .all()
    )

    return jsonify(
        {
            "transactions": [
                serialize_transaction(transaction)
                for transaction in transactions
            ]
        }
    ), 200


def serialize_offer(offer):
    """Convert an Offer object into JSON-safe data."""

    return {
        "id": offer.id,
        "listing_id": offer.listing_id,
        "buyer_id": offer.buyer_id,
        "offer_price": (
            float(offer.offer_price)
            if offer.offer_price is not None
            else None
        ),
        "swap_listing_id": offer.swap_listing_id,
        "status": offer.status,
        "created_at": (
            offer.created_at.isoformat()
            if offer.created_at
            else None
        ),
    }                                                                                               


def serialize_transaction(transaction):
    """Convert a Transaction object into JSON-safe data."""

    return {
        "id": transaction.id,
        "listing_id": transaction.listing_id,
        "buyer_id": transaction.buyer_id,
        "seller_id": transaction.seller_id,
        "completed_at": (
            transaction.completed_at.isoformat()
            if transaction.completed_at
            else None
        ),
    }