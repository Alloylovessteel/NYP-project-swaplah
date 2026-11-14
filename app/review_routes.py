"""Review routes."""

from flask import Blueprint, request, jsonify, session, render_template
from .auth import login_required_redirect, admin_required
from .models import db, Review, Transaction
from .review_service import (
    validate_rating,
    validate_comment,
    calculate_average_rating,
    review_exists,
    get_counterpart_id
)

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/api/reviews", methods=["POST"])
def create_review():
    """Create a review for the other party on a completed transaction.

    The reviewer is always taken from the session (not the request body)
    so a user cannot post a review pretending to be someone else. The
    reviewee is validated against the transaction's buyer/seller so a
    review can only be left for the actual counterpart on that deal.
    """
    reviewer_id = session.get("user_id")
    if not reviewer_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}

    transaction_id = data.get("transaction_id")
    if not transaction_id:
        return jsonify({"error": "transaction_id is required"}), 400

    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction not found"}), 404

    expected_reviewee_id = get_counterpart_id(transaction, reviewer_id)
    if expected_reviewee_id is None:
        return jsonify({
            "error": "You are not a participant in this transaction"
        }), 403

    reviewee_id = data.get("reviewee_id", expected_reviewee_id)
    if reviewee_id != expected_reviewee_id:
        return jsonify({
            "error": "reviewee_id does not match the other party on this transaction"
        }), 400

    rating = data.get("rating")
    comment = data.get("comment")

    valid, error = validate_rating(rating)
    if not valid:
        return jsonify({"error": error}), 400

    valid, error = validate_comment(comment)
    if not valid:
        return jsonify({"error": error}), 400

    if review_exists(Review, transaction_id, reviewer_id):
        return jsonify({
            "error": "Review already exists"
        }), 400

    review = Review(
        transaction_id=transaction_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        rating=rating,
        comment=comment
    )

    try:
        db.session.add(review)
        db.session.commit()

        return jsonify({
            "message": "Review created successfully",
            "review": review.to_dict()
        }), 201

    except Exception as exc:
        db.session.rollback()

        return jsonify({
            "error": str(exc)
        }), 500


@review_bp.route(
    "/api/users/<int:user_id>/reviews",
    methods=["GET"]
)
def get_user_reviews(user_id):
    """Return a user's review summary and review list.

    Any user (logged in or not) can view another user's average
    rating and reviews - this powers the seller rating shown on the
    listing detail page.
    """

    reviews = Review.query.filter_by(
        reviewee_id=user_id,
        is_deleted=False
    ).order_by(Review.created_at.desc()).all()

    if not reviews:
        return jsonify({
            "message": "No ratings yet (New Trader)",
            "average_rating": None,
            "review_count": 0,
            "reviews": []
        }), 200

    average = calculate_average_rating(reviews)

    return jsonify({
        "average_rating": average,
        "review_count": len(reviews),
        "reviews": [review.to_dict() for review in reviews]
    }), 200


@review_bp.route("/api/reviews/pending", methods=["GET"])
def get_pending_reviews():
    """Return the logged-in user's completed transactions that are
    still awaiting a review from them.

    Used to drive the "Leave a review" list on the transaction
    history page - it does not replace Ashlyn's full transaction
    history endpoint, it only surfaces what still needs a review.
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    transactions = Transaction.query.filter(
        (Transaction.buyer_id == user_id) | (Transaction.seller_id == user_id)
    ).order_by(Transaction.completed_at.desc()).all()

    pending = []
    for transaction in transactions:
        if review_exists(Review, transaction.id, user_id):
            continue

        counterpart_id = get_counterpart_id(transaction, user_id)
        if transaction.buyer_id == user_id:
            counterpart = transaction.seller
            role = "buyer"
        else:
            counterpart = transaction.buyer
            role = "seller"

        pending.append({
            "transaction_id": transaction.id,
            "listing_id": transaction.listing_id,
            "listing_title": transaction.listing.title if transaction.listing else None,
            "completed_at": transaction.completed_at.isoformat(),
            "your_role": role,
            "counterpart_id": counterpart_id,
            "counterpart_display_name": counterpart.display_name if counterpart else None
        })

    return jsonify({"user_id": user_id, "pending_reviews": pending}), 200


@review_bp.route("/transaction-history")
@login_required_redirect
def transaction_history_page():
    """Render the transaction history / reviews page."""
    return render_template("transaction_history.html")


@review_bp.route("/api/admin/reviews", methods=["GET"])
@admin_required
def get_all_reviews():
    """Return every review (including admin-deleted ones) for moderation."""
    reviews = Review.query.order_by(Review.created_at.desc()).all()

    result = []
    for review in reviews:
        data = review.to_dict()
        data["reviewee_display_name"] = review.reviewee.display_name if review.reviewee else None
        result.append(data)

    return jsonify(result), 200


@review_bp.route("/api/admin/reviews/<int:review_id>/delete", methods=["PUT"])
@admin_required
def admin_delete_review(review_id):
    """Soft-delete a review: hide it from the marketplace without removing
    it from the database, and lock it against further admin action.
    """
    review = db.get_or_404(Review, review_id)

    if review.is_deleted:
        return jsonify({"error": "This review has already been deleted"}), 400

    review.is_deleted = True
    db.session.commit()

    return jsonify({
        "message": "Review deleted successfully",
        "review": review.to_dict()
    }), 200


@review_bp.route("/admin/reviews")
@admin_required
def admin_reviews_page():
    """Render the review moderation page."""
    return render_template("admin_reviews.html", is_admin=True)