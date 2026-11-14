"""Routes for transactions."""

from flask import Blueprint, jsonify, session
from .models import Transaction


transactions_bp = Blueprint('transactions', __name__)


@transactions_bp.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get transactions. Login required."""

    user_id = session.get('user_id')

    if not user_id:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    transactions = Transaction.query.filter(
        (Transaction.buyer_id == user_id) |
        (Transaction.seller_id == user_id)
    ).order_by(Transaction.completed_at.desc()).all()

    result = []
    for transaction in transactions:
        is_buyer = transaction.buyer_id == user_id
        counterpart = transaction.seller if is_buyer else transaction.buyer

        result.append({
            "id": transaction.id,
            "listing_id": transaction.listing_id,
            "listing_title": transaction.listing.title if transaction.listing else None,
            "buyer_id": transaction.buyer_id,
            "seller_id": transaction.seller_id,
            "role": "buyer" if is_buyer else "seller",
            "counterpart_name": counterpart.display_name if counterpart else None,
            "completed_at": transaction.completed_at.isoformat()
        })

    return jsonify(result), 200