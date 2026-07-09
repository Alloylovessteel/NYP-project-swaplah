"""Unit tests for User Registration (issue #50).

These test the validation logic and model layer directly,
without going through the HTTP layer (see tests/api/ for that).
"""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app
from app.models import db, User
from app.auth import is_nyp_email


@pytest.fixture
def app():
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
    }
    flask_app = create_app(test_config)
    yield flask_app
    with flask_app.app_context():
        db.session.remove()
        db.drop_all()


# --- is_nyp_email ---

def test_is_nyp_email_accepts_nyp_domain():
    assert is_nyp_email("student@nyp.edu.sg") is True


def test_is_nyp_email_accepts_mymail_subdomain():
    assert is_nyp_email("student@mymail.nyp.edu.sg") is True


def test_is_nyp_email_rejects_other_domains():
    assert is_nyp_email("student@gmail.com") is False


def test_is_nyp_email_rejects_malformed_email():
    assert is_nyp_email("not-an-email") is False


def test_is_nyp_email_rejects_similar_looking_domain():
    """Guards against e.g. 'nyp.edu.sg.evil.com' style bypass attempts."""
    assert is_nyp_email("student@nyp.edu.sg.fake.com") is False


# --- Password hashing ---

def test_password_is_hashed_not_plaintext():
    hashed = generate_password_hash("Secret123!")
    assert hashed != "Secret123!"
    assert check_password_hash(hashed, "Secret123!")


# --- Duplicate detection at the model layer ---

def test_duplicate_email_detected(app):
    with app.app_context():
        user = User(
            student_id="S1000001", first_name="John", last_name="Tan",
            display_name="Johnny", email="john@nyp.edu.sg",
            contact_number="91234567",
            password_hash=generate_password_hash("Secret123!")
        )
        db.session.add(user)
        db.session.commit()

        existing = User.query.filter_by(email="john@nyp.edu.sg").first()
        assert existing is not None
        assert existing.student_id == "S1000001"


def test_no_duplicate_when_email_not_registered(app):
    with app.app_context():
        existing = User.query.filter_by(email="nobody@nyp.edu.sg").first()
        assert existing is None


def test_duplicate_student_id_detected(app):
    with app.app_context():
        user = User(
            student_id="S1000002", first_name="Amy", last_name="Lee",
            display_name="Amy L", email="amy@nyp.edu.sg",
            contact_number="98765432",
            password_hash=generate_password_hash("Pass1234!")
        )
        db.session.add(user)
        db.session.commit()

        existing = User.query.filter_by(student_id="S1000002").first()
        assert existing is not None
