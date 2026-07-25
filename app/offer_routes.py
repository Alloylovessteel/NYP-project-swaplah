"""Routes for offers and transactions."""
from flask import Blueprint, request, jsonify, session
from .models import db, Offer, Listing, User, Transaction
from datetime import datetime, timezone

offers_bp = Blueprint('offers', __name__)


@offers_bp.route('/api/offers', methods=['POST'])
def create_offer():
    """Submit an offer on a listing."""
    buyer_id = session.get('user_id')
    if not buyer_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    listing_id = data.get('listing_id')
    offer_price = data.get('offer_price')
    swap_listing_id = data.get('swap_listing_id')
    
    if not listing_id:
        return jsonify({"error": "listing_id is required"}), 400
    
    # Must have either price or swap listing
    if not offer_price and not swap_listing_id:
        return jsonify({"error": "offer_price or swap_listing_id is required"}), 400
    
    listing = Listing.query.get(listing_id)
    if not listing or listing.is_deleted:
        return jsonify({"error": "Listing not found"}), 404
    
    # Cannot offer on own listing
    if listing.seller_id == buyer_id:
        return jsonify({"error": "Cannot offer on your own listing"}), 400
    
    # If swap, verify swap listing exists and belongs to buyer
    if swap_listing_id:
        swap_listing = Listing.query.get(swap_listing_id)
        if not swap_listing or swap_listing.is_deleted:
            return jsonify({"error": "Swap listing not found"}), 404
        if swap_listing.seller_id != buyer_id:
            return jsonify({"error": "Swap listing must belong to you"}), 400
    
    offer = Offer(
        listing_id=listing_id,
        buyer_id=buyer_id,
        offer_price=offer_price,
        swap_listing_id=swap_listing_id,
        status='pending'
    )
    
    try:
        db.session.add(offer)
        db.session.commit()
        return jsonify({
            "message": "Offer submitted successfully",
            "offer_id": offer.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@offers_bp.route('/api/listings/<listing_id>/offers', methods=['GET'])
def get_offers_for_listing(listing_id):
    """Get pending offers for a listing (seller only)."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    listing = Listing.query.get(listing_id)
    if not listing:
        return jsonify({"error": "Listing not found"}), 404
    
    # Only seller can view offers on their listing
    if listing.seller_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    offers = Offer.query.filter_by(
        listing_id=listing_id,
        status='pending'
    ).all()
    
    return jsonify([
        {
            "id": offer.id,
            "buyer_id": offer.buyer_id,
            "buyer_display_name": offer.buyer.display_name if offer.buyer else None,
            "offer_price": offer.offer_price,
            "swap_listing_id": offer.swap_listing_id,
            "status": offer.status,
            "created_at": offer.created_at.isoformat()
        }
        for offer in offers
    ]), 200


@offers_bp.route('/api/offers/<int:offer_id>', methods=['PUT'])
def respond_to_offer(offer_id):
    """Accept or reject an offer."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    offer = Offer.query.get(offer_id)
    if not offer:
        return jsonify({"error": "Offer not found"}), 404
    
    # Only listing seller can respond to offer
    listing = Listing.query.get(offer.listing_id)
    if listing.seller_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    
    data = request.get_json()
    action = data.get('action')  # 'accept' or 'reject'
    
    if action not in ['accept', 'reject']:
        return jsonify({"error": "action must be 'accept' or 'reject'"}), 400
    
    if action == 'reject':
        offer.status = 'rejected'
        db.session.commit()
        return jsonify({"message": "Offer rejected"}), 200
    
    if action == 'accept':
        # Accept this offer
        offer.status = 'accepted'
        
        # Auto-reject all other pending offers on same listing
        other_offers = Offer.query.filter(
            Offer.listing_id == offer.listing_id,
            Offer.id != offer_id,
            Offer.status == 'pending'
        ).all()
        
        for other_offer in other_offers:
            other_offer.status = 'rejected'
        
        # Create transaction record
        transaction = Transaction(
            listing_id=offer.listing_id,
            buyer_id=offer.buyer_id,
            seller_id=listing.seller_id,
            completed_at=datetime.now(timezone.utc)
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "message": "Offer accepted",
            "transaction_id": transaction.id
        }), 200
    
    return jsonify({"error": "Invalid action"}), 400


@offers_bp.route('/api/user/offers', methods=['GET'])
def get_user_offers():
    """Get all offers made by logged-in user."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    offers = Offer.query.filter_by(buyer_id=user_id).all()
    
    return jsonify([
        {
            "id": offer.id,
            "listing_id": offer.listing_id,
            "listing_title": offer.listing.title if offer.listing else None,
            "offer_price": offer.offer_price,
            "swap_listing_id": offer.swap_listing_id,
            "status": offer.status,
            "created_at": offer.created_at.isoformat()
        }
        for offer in offers
    ]), 200