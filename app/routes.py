"""Routes for the Listings management."""
from flask import Blueprint, request, jsonify
from .models import db, Listing

# Create a Blueprint for listings
listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/api/listings', methods=['POST'])
def create_listing():
    """Create a new item listing."""
    data = request.get_json()
    required_fields = ['title', 'description', 'price', 'category', 'condition', 'image_url']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Field '{field}' is required"}), 400

    new_listing = Listing(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        category=data['category'],
        condition=data['condition'],
        image_url=data['image_url']
    )

    try:
        db.session.add(new_listing)
        db.session.commit()
        return jsonify(new_listing.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@listings_bp.route('/api/listings', methods=['GET'])
def get_listings():
    """Returns active listings with search, filter, and pagination."""
    # 1. Base query: only show non-deleted items
    query = Listing.query.filter_by(is_deleted=False)

    # 2. Keyword Search (Title and Description) - Requirement Page 2, C.vii
    search_query = request.args.get('search')
    if search_query:
        query = query.filter(
            (Listing.title.ilike(f'%{search_query}%')) | 
            (Listing.description.ilike(f'%{search_query}%'))
        )

    # 3. Filter by Category and Condition - Requirement Page 2, C.viii
    category_filter = request.args.get('category')
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    condition_filter = request.args.get('condition')
    if condition_filter:
        query = query.filter_by(condition=condition_filter)

    # 4. Sorting: Newest first - Requirement Page 2, C.vii
    query = query.order_by(Listing.listing_date.desc())

    # 5. Pagination: 10 items per page - Requirement Page 2, C.vi
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return jsonify({
        "listings": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@listings_bp.route('/api/listings/<listing_id>', methods=['GET'])
def get_listing_detail(listing_id):
    """Returns a single listing by ID with seller details."""
    listing = db.get_or_404(Listing, listing_id)
    
    if listing.is_deleted:
        return jsonify({"error": "Listing not found"}), 404

    result = listing.to_dict()
    
    # Show Seller Name, Email, and Phone
    if listing.seller:
        result['seller_info'] = {
            "display_name": listing.seller.display_name,
            "email": listing.seller.email,
            "contact_number": listing.seller.contact_number
        }
    
    return jsonify(result), 200

@listings_bp.route('/api/listings/<listing_id>', methods=['PUT'])
def update_listing(listing_id):
    """Updates an existing listing (owner only)."""
    listing = db.get_or_404(Listing, listing_id)

    # Only the seller can edit/delete
    # (Note: I will add strict auth check once Shamreen finishes User Auth)

    if listing.is_deleted:
        return jsonify({"error": "Cannot edit a deleted listing"}), 404

    data = request.get_json()

    # Update allowed fields
    if 'title' in data:
        listing.title = data['title']
    if 'description' in data:
        listing.description = data['description']
    if 'price' in data:
        listing.price = data['price']
    if 'category' in data:
        listing.category = data['category']
    if 'condition' in data:
        listing.condition = data['condition']
    if 'image_url' in data:
        listing.image_url = data['image_url']

    db.session.commit()
    return jsonify(listing.to_dict()), 200

@listings_bp.route('/api/listings/<listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    """Soft-deletes a listing by setting is_deleted to True."""
    listing = db.get_or_404(Listing, listing_id)

    # Deletion is a soft delete
    listing.is_deleted = True
    db.session.commit()

    return jsonify({"message": "Listing successfully deleted"}), 200
