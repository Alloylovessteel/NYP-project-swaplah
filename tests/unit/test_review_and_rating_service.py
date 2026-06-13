"""Tests for review service."""

from app.review_service import (
    validate_rating,
    validate_comment,
    calculate_average_rating
)


class MockReview:
    """Mock review."""

    def __init__(self, rating):
        self.rating = rating


def test_no_reviews():
    assert calculate_average_rating([]) is None


def test_average_calculation():
    reviews = [
        MockReview(5),
        MockReview(4),
        MockReview(3)
    ]

    assert calculate_average_rating(reviews) == 4.0


def test_average_rounding():
    reviews = [
        MockReview(5),
        MockReview(4),
        MockReview(4)
    ]

    assert calculate_average_rating(reviews) == 4.3


def test_invalid_rating_none():
    valid, _ = validate_rating(None)
    assert not valid


def test_rating_below_range():
    valid, _ = validate_rating(0)
    assert not valid


def test_rating_above_range():
    valid, _ = validate_rating(6)
    assert not valid


def test_comment_too_long():
    valid, _ = validate_comment("a" * 501)
    assert not valid