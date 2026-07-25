"""Routes for the Listings management."""
from flask import Blueprint, request, jsonify, render_template, session, redirect
from .models import db, Listing, Report, User
from .auth import admin_required, login_required_redirect


# Create a Blueprint for listings
listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/api/listings', methods=['POST'])
def create_listing():
    """Create a new item listing."""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    required_fields = ['title', 'description', 'price', 'category', 'condition', 'image_url']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Field '{field}' is required"}), 400

    # --- PRICE VALIDATION LOGIC ---
    price_str = str(data['price']).strip()

    # Check if price is NOT "Free", NOT "Swap Only", and NOT a valid float number
    is_free_or_swap = price_str.lower() in ["free", "swap only"]
    is_valid_number = True
    try:
        float(price_str)
    except ValueError:
        is_valid_number = False

    if not is_free_or_swap and not is_valid_number:
        return jsonify({"error": "Price must be a valid number, 'Free', or 'Swap Only'"}), 400
    # ------------------------------

    new_listing = Listing(
        title=data['title'],
        description=data['description'],
        price=price_str, # Save the validated string
        category=data['category'],
        condition=data['condition'],
        image_url=data['image_url'],
        seller_id=user_id
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
        if listing.seller_id != session.get('user_id'):
            return jsonify({"error": "Forbidden"}), 403
        data = request.get_json()
        fields = ['title', 'description', 'price', 'category', 'condition', 'image_url']
        for field in fields:
            if field in data:
                setattr(listing, field, data[field])
        db.session.commit()
        return jsonify(listing.to_dict()), 200

    # 3. DELETE: Soft-delete
    if request.method == 'DELETE':
        if listing.seller_id != session.get('user_id'):
            return jsonify({"error": "Forbidden"}), 403
        listing.is_deleted = True
        db.session.commit()
        return jsonify({"message": "Listing successfully deleted"}), 200

@listings_bp.route('/marketplace')
@login_required_redirect
def marketplace_page():
    """Render the Marketplace HTML page."""
    return render_template('listings.html')

@listings_bp.route('/create-listing')
@login_required_redirect
def create_listing_page():
    """Render the Create Listing HTML page."""
    return render_template('create_listing.html')

@listings_bp.route('/listings/<listing_id>')
@login_required_redirect
def listing_detail_page(listing_id):
    """Render the Listing Detail HTML page."""
    return render_template('listing_detail.html', listing_id=listing_id)

@listings_bp.route('/edit-listing/<listing_id>')
@login_required_redirect
def edit_listing_page(listing_id):
    """Render the Edit Listing HTML page."""
    return render_template('edit_listing.html', listing_id=listing_id)

# Reports
    ...

# Reports
@listings_bp.route('/api/reports', methods=['POST'])
def create_report():
    """Submit a report for a listing."""

    data = request.get_json()

    required_fields = ['listing_id', 'reason', 'description']

    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({
                "error": f"Field '{field}' is required"
            }), 400

    listing = Listing.query.filter_by(
        id=data['listing_id'],
        is_deleted=False
    ).first()

    if not listing:
        return jsonify({
            "error": "Listing not found"
        }), 404

    report = Report(
        listing_id=data['listing_id'],
        reason=data['reason'],
        description=data['description']
    )

    try:
        db.session.add(report)
        db.session.commit()

        return jsonify({
            "message": "Report submitted successfully"
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500
    
@listings_bp.route('/api/admin/reports', methods=['GET'])
@admin_required
def get_reports():
    """Return all submitted reports."""

    reports = Report.query.order_by(
        Report.created_at.desc()
    ).all()

    return jsonify(
        [report.to_dict() for report in reports]
    ), 200

@listings_bp.route('/admin/reports')
@admin_required
def reports_page():
    """Render reports management page."""

    return render_template(
        'reports.html',
        is_admin=True
    )

@listings_bp.route('/api/admin/reports/<int:report_id>', methods=['DELETE'])
@admin_required
def dismiss_report(report_id):
    """Dismiss a report."""

    report = db.get_or_404(Report, report_id)

    db.session.delete(report)
    db.session.commit()

    return jsonify({
        "message": "Report dismissed successfully"
    }), 200

@listings_bp.route('/admin/users')
@admin_required
def users_page():
    """Render user management page."""

    return render_template(
        'users.html',
        is_admin=True
    )

@listings_bp.route('/api/admin/users/<int:user_id>/suspend', methods=['PUT'])
@admin_required
def suspend_user(user_id):
    """Suspend a user account."""

    user = db.get_or_404(User, user_id)

    user.account_status = "suspended"
    db.session.commit()

    return jsonify({
        "message": "User suspended successfully"
    }), 200

@listings_bp.route('/api/admin/users/<int:user_id>/unsuspend', methods=['PUT'])
@admin_required
def unsuspend_user(user_id):
    """Unsuspend a user account."""

    user = db.get_or_404(User, user_id)

    user.account_status = "active"
    db.session.commit()

    return jsonify({
        "message": "User unsuspended successfully"
    }), 200