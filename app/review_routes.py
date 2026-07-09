"""Review routes."""

from flask import Blueprint, request, jsonify

from .models import db, Review
from .review_service import (
    validate_rating,
    validate_comment,
    calculate_average_rating,
    review_exists
)

review_bp = Blueprint("reviews", __name__)


@review_bp.route("/api/reviews", methods=["POST"])
def create_review():
    """Create a review."""
    data = request.get_json()

    rating = data.get("rating")
    comment = data.get("comment")

    valid, error = validate_rating(rating)
    if not valid:
        return jsonify({"error": error}), 400

    valid, error = validate_comment(comment)
    if not valid:
        return jsonify({"error": error}), 400

    if review_exists(
        Review,
        data["transaction_id"],
        data["reviewer_id"]
    ):
        return jsonify({
            "error": "Review already exists"
        }), 400

    review = Review(
        transaction_id=data["transaction_id"],
        reviewer_id=data["reviewer_id"],
        reviewee_id=data["reviewee_id"],
        rating=rating,
        comment=comment
    )

    try:
        db.session.add(review)
        db.session.commit()

        return jsonify({
            "message": "Review created successfully"
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
    """Return user review summary."""

    reviews = Review.query.filter_by(
        reviewee_id=user_id
    ).all()

    if not reviews:
        return jsonify({
            "message": "No ratings yet (New Trader)",
            "review_count": 0
        }), 200

    average = calculate_average_rating(reviews)

    return jsonify({
        "average_rating": average,
        "review_count": len(reviews)
    }), 200