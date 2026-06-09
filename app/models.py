"""Database models for the SwapLah application."""
from datetime import datetime, timezone
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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
    last_modified = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    is_deleted = db.Column(db.Boolean, default=False)

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
            "last_modified": self.last_modified.isoformat()
        }