"""Unit tests for User Login and Logout (issue #51)."""
import pytest
from werkzeug.security import generate_password_hash, check_password_hash

from app import create_app
from app.models import db, User


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


def test_new_user_defaults_to_active_status(app):
    with app.app_context():
        user = User(
            student_id="S3000001", first_name="Tim", last_name="Ong",
            display_name="Tim O", email="tim@nyp.edu.sg",
            contact_number="91112222",
            password_hash=generate_password_hash("Secret123!")
        )
        db.session.add(user)
        db.session.commit()
        assert user.account_status == 'active'


def test_correct_password_verifies(app):
    with app.app_context():
        user = User(
            student_id="S3000002", first_name="Sue", last_name="Lim",
            display_name="Sue L", email="sue@nyp.edu.sg",
            contact_number="93334444",
            password_hash=generate_password_hash("MyPass123!")
        )
        db.session.add(user)
        db.session.commit()
        assert check_password_hash(user.password_hash, "MyPass123!") is True


def test_wrong_password_does_not_verify(app):
    with app.app_context():
        user = User(
            student_id="S3000003", first_name="Bob", last_name="Tan",
            display_name="Bob T", email="bob@nyp.edu.sg",
            contact_number="95556666",
            password_hash=generate_password_hash("CorrectPass1")
        )
        db.session.add(user)
        db.session.commit()
        assert check_password_hash(user.password_hash, "WrongPass1") is False
