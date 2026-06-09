"""Database models for the SwapLah application."""
from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Listing(db.Model):
    """Model representing an item listing in the marketplace."""
    __tablename__ = 'listings'

    # Primary Key using UUID for 'Unique ID' requirement
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.String(20), nullable=False)  # Handles "Free" or "Swap Only"
    category = db.Column(db.String(50), nullable=False)
    condition = db.Column(db.String(20), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    
    # Date & Timestamp requirements from Page 2
    listing_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft Delete requirement from Page 2
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