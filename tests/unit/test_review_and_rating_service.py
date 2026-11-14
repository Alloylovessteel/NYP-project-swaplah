"""Tests for review service."""

from app.review_service import (
    validate_rating,
    validate_comment,
    calculate_average_rating,
    get_counterpart_id
)


class MockReview:
    """Mock review."""

    def __init__(self, rating):
        self.rating = rating


class MockTransaction:
    """Mock transaction with buyer_id/seller_id only."""

    def __init__(self, buyer_id, seller_id):
        self.buyer_id = buyer_id
        self.seller_id = seller_id


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


def test_counterpart_id_for_buyer():
    txn = MockTransaction(buyer_id=1, seller_id=2)
    assert get_counterpart_id(txn, 1) == 2


def test_counterpart_id_for_seller():
    txn = MockTransaction(buyer_id=1, seller_id=2)
    assert get_counterpart_id(txn, 2) == 1


def test_counterpart_id_for_non_participant():
    txn = MockTransaction(buyer_id=1, seller_id=2)
    assert get_counterpart_id(txn, 999) is None