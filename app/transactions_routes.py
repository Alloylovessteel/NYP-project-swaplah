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
    ).all()

    return jsonify([
        {
            "id": transaction.id,
            "listing_id": transaction.listing_id,
            "buyer_id": transaction.buyer_id,
            "seller_id": transaction.seller_id,
            "completed_at": transaction.completed_at.isoformat()
        }
        for transaction in transactions
    ]), 200