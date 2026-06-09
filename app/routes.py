"""Routes for the Listings management."""
from flask import Blueprint, request, jsonify
from .models import db, Listing

# Create a Blueprint for listings
listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/api/listings', methods=['POST'])
def create_listing():
    """Create a new item listing. Expects JSON: title, description, price, category, condition, image_url"""
    data = request.get_json()

    # 1. Server-side Validation
    required_fields = ['title', 'description', 'price', 'category', 'condition', 'image_url']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Field '{field}' is required"}), 400

    # 2. Create the Listing object
    # The ID, date, and timestamps are handled automatically by the model
    new_listing = Listing(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        category=data['category'],
        condition=data['condition'],
        image_url=data['image_url']
    )

    # 3. Save to Database
    try:
        db.session.add(new_listing)
        db.session.commit()
        # Return the created listing as JSON with 201 Created status
        return jsonify(new_listing.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500
