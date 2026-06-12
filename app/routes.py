"""Routes for the Listings management."""
from flask import Blueprint, request, jsonify, render_template
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
        image_url=data['image_url'],
        seller_id=1 # Temporary
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
    query = Listing.query.filter_by(is_deleted=False)

    search_query = request.args.get('search')
    if search_query:
        query = query.filter(
            (Listing.title.ilike(f'%{search_query}%')) | 
            (Listing.description.ilike(f'%{search_query}%'))
        )

    category_filter = request.args.get('category')
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    condition_filter = request.args.get('condition')
    if condition_filter:
        query = query.filter_by(condition=condition_filter)

    query = query.order_by(Listing.listing_date.desc())

    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return jsonify({
        "listings": [item.to_dict() for item in pagination.items],
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200

@listings_bp.route('/api/listings/<listing_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_listing(listing_id):
    """Handles fetching, updating, and deleting a single listing."""
    listing = db.get_or_404(Listing, listing_id)
    
    # 1. GET: Fetch Details
    if request.method == 'GET':
        if listing.is_deleted:
            return jsonify({"error": "Listing not found"}), 404
        result = listing.to_dict()
        if listing.seller:
            result['seller_info'] = {
                "display_name": listing.seller.display_name,
                "email": listing.seller.email,
                "contact_number": listing.seller.contact_number
            }
        return jsonify(result), 200

    # 2. PUT: Update Listing
    if request.method == 'PUT':
        if listing.is_deleted:
            return jsonify({"error": "Cannot edit a deleted listing"}), 404
        data = request.get_json()
        fields = ['title', 'description', 'price', 'category', 'condition', 'image_url']
        for field in fields:
            if field in data:
                setattr(listing, field, data[field])
        db.session.commit()
        return jsonify(listing.to_dict()), 200

    # 3. DELETE: Soft-delete
    if request.method == 'DELETE':
        listing.is_deleted = True
        db.session.commit()
        return jsonify({"message": "Listing successfully deleted"}), 200

@listings_bp.route('/marketplace')
def marketplace_page():
    """Render the Marketplace HTML page."""
    return render_template('listings.html')

@listings_bp.route('/create-listing')
def create_listing_page():
    """Render the Create Listing HTML page."""
    return render_template('create_listing.html')

@listings_bp.route('/listings/<listing_id>')
def listing_detail_page(listing_id):
    """Render the Listing Detail HTML page."""
    return render_template('listing_detail.html', listing_id=listing_id)

@listings_bp.route('/edit-listing/<listing_id>')
def edit_listing_page(listing_id):
    """Render the Edit Listing HTML page."""
    return render_template('edit_listing.html', listing_id=listing_id)



@bp.route('/api/reviews', methods=['POST'])
def leave_review():
    """AC-1 to AC-4: Handles submitting a review for a completed trade."""
    data = request.get_json() or {}
    tx_id = data.get('transaction_id')
    reviewer_id = data.get('reviewer_id')
    reviewee_id = data.get('reviewee_id')
    rating = data.get('rating')
    comment = data.get('comment', '')

    # AC-2: Input validation constraints
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400
    if len(comment) > 500:
        return jsonify({"error": "Comment must not exceed 500 characters"}), 400

    # AC-1: Gating mechanism - Verify transaction exists in the DB
    tx_record = Transaction.query.get(tx_id)
    if not tx_record:
        return jsonify({"error": "Transaction not found or not completed"}), 404

    try:
        new_review = Review(
            transaction_id=tx_id, reviewer_id=reviewer_id,
            reviewee_id=reviewee_id, rating=rating, comment=comment
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": "Review submitted successfully!"}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Duplicate submission detected for this transaction"}), 409


@bp.route('/api/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    """AC-1, AC-3, AC-4: Fetches individual reviews and computes the arithmetic mean."""
    user_reviews = Review.query.filter_by(reviewee_id=user_id).all()
    total = len(user_reviews)

    # AC-4: Null state exception handling for unrated new traders
    if total == 0:
        return jsonify({
            "average_rating_display": "No ratings yet (New Trader)",
            "numeric_rating": None, "total_reviews": 0, "reviews": []
        }), 200

    # AC-1 & AC-3: Calculate arithmetic mean and round strictly to 1 decimal place
    scores = [r.rating for r in user_reviews]
    avg_score = round(sum(scores) / total, 1)

    reviews_data = [
        {"reviewer_id": r.reviewer_id, "rating": r.rating, "comment": r.comment}
        for r in user_reviews
    ]
    return jsonify({
        "average_rating_display": f"⭐ {avg_score:.1f} / 5.0",
        "numeric_rating": avg_score, "total_reviews": total, "reviews": reviews_data
    }), 200
