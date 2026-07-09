"""Business logic for Review & Rating feature."""

from typing import List


def validate_rating(rating):
    """Validate rating value."""
    if rating is None:
        return False, "Rating is required"

    if not isinstance(rating, int):
        return False, "Rating must be an integer"

    if rating < 1 or rating > 5:
        return False, "Rating must be between 1 and 5"

    return True, None


def validate_comment(comment):
    """Validate optional comment."""
    if comment is None:
        return True, None

    if len(comment) > 500:
        return False, "Comment cannot exceed 500 characters"

    return True, None


def calculate_average_rating(reviews: List):
    """Calculate average rating."""
    if not reviews:
        return None

    average = sum(review.rating for review in reviews) / len(reviews)
    return round(average, 1)


def review_exists(review_model, transaction_id, reviewer_id):
    """Check whether duplicate review exists."""
    return review_model.query.filter_by(
        transaction_id=transaction_id,
        reviewer_id=reviewer_id
    ).first() is not None