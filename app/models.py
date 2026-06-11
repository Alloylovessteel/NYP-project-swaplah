"""Database models for the SwapLah application."""
from datetime import datetime, timezone
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Model representing a student user."""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    account_status = db.Column(db.String(20), default='active')
    listings = db.relationship('Listing', backref='seller', lazy=True)


class Listing(db.Model):
    """Model representing an item listing in the marketplace."""
    __tablename__ = 'listings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

    listing_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_modified = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    is_deleted = db.Column(db.Boolean, default=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        """Convert model instance to dictionary for JSON responses."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "condition": self.condition,
            "image_url": self.image_url,
            "listing_date": self.listing_date.isoformat(),
            "last_modified": self.last_modified.isoformat(),
            "seller_id": self.seller_id
        }
    
class Offer(db.Model):
    """Model representing an offer made on a listing."""
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)

    listing_id = db.Column(
        db.String(36),
        db.ForeignKey('listings.id'),
        nullable=False
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    offer_price = db.Column(db.String(20))

    swap_listing_id = db.Column(
        db.String(36),
        db.ForeignKey('listings.id'),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default='pending'
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )


class Transaction(db.Model):
    """Completed transaction history."""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)

    listing_id = db.Column(
        db.String(36),
        db.ForeignKey('listings.id'),
        nullable=False
    )

    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    seller_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    completed_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )