"""Routes for user account management."""
import re
import secrets
from functools import wraps
from flask import Blueprint, request, jsonify, session, render_template, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, Listing

auth_bp = Blueprint('auth', __name__)

reset_tokens = {}


@auth_bp.before_app_request
def check_session_and_requests():
    """Check sessions, report access, and availability of offered items."""
    user_id = session.get('user_id')
    if user_id:
        user = db.session.get(User, user_id)
        if not user or user.account_status == 'suspended':
            suspended = user is not None
            session.clear()
            public_endpoints = {
                'static', 'health_check',
                'auth.login_page', 'auth.login',
                'auth.admin_login_page', 'auth.admin_login',
                'auth.logout_page', 'auth.logout', 'auth.admin_logout',
            }
            if request.endpoint not in public_endpoints:
                if request.path.startswith('/api/'):
                    message = 'Your account has been suspended' if suspended else 'Unauthorized'
                    return jsonify({'error': message}), 403 if suspended else 401
                return redirect('/admin/login' if request.path.startswith('/admin') else '/login')

    if request.method == 'POST' and request.endpoint == 'listings.create_report':
        if not session.get('user_id'):
            return jsonify({'error': 'Unauthorized'}), 401

    if (request.method == 'POST' and request.endpoint == 'offers.create_offer'
            and session.get('user_id')):
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            for field, error in (
                ('listing_id', 'Listing not found'),
                ('swap_listing_id', 'Swap listing not found'),
            ):
                listing_id = data.get(field)
                if isinstance(listing_id, (str, int, float)) and not isinstance(listing_id, bool):
                    listing = db.session.get(Listing, str(listing_id))
                    if listing and listing.is_deleted:
                        return jsonify({'error': error}), 404

    return None


def is_nyp_email(email):
    """Check if email is a valid NYP email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@(nyp\.edu\.sg|mymail\.nyp\.edu\.sg)$'
    return re.match(pattern, email) is not None


def admin_required(f):
    """Decorator to check if user is an admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Unauthorized"}), 401

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        if not user.is_admin:
            return jsonify({"error": "Forbidden - Admin access required"}), 403

        return f(*args, **kwargs)
    return decorated_function


def login_required_redirect(f):
    """Decorator to redirect unauthenticated users to login page."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """Register a new student user."""
    data = request.get_json()
    required_fields = ['student_id', 'first_name', 'last_name',
                       'display_name', 'email', 'contact_number', 'password']
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Field '{field}' is required"}), 400

    if not is_nyp_email(data['email']):
        return jsonify({"error": "Only NYP email addresses are accepted"}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "Email already registered"}), 400

    if User.query.filter_by(student_id=data['student_id']).first():
        return jsonify({"error": "Student ID already registered"}), 400

    new_user = User(
        student_id=data['student_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        display_name=data['display_name'],
        email=data['email'],
        contact_number=data['contact_number'],
        password_hash=generate_password_hash(data['password'])
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Registration successful"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """Login a registered user."""
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.is_admin:
        return jsonify({
            "error": "Please use the Administrator Login page."
        }), 403

    if user.account_status == "suspended":
        return jsonify({
            "error": "Your account has been suspended"
        }), 403

    session.permanent = True
    session["user_id"] = user.id

    return jsonify({
        "message": "Login successful",
        "user_id": user.id
    }), 200


@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Logout the current user."""
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route('/api/profile', methods=['GET'])
def view_profile():
    """View the logged-in user's profile."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "student_id": user.student_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "display_name": user.display_name,
        "email": user.email,
        "contact_number": user.contact_number
    }), 200


@auth_bp.route('/api/profile', methods=['PUT'])
def edit_profile():
    """Edit the logged-in user's profile."""
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'display_name' in data:
        user.display_name = data['display_name']
    if 'contact_number' in data:
        user.contact_number = data['contact_number']
    if 'password' in data and data['password']:
        if not data.get('current_password'):
            return jsonify({"error": "Current password is required"}), 400
        if not check_password_hash(user.password_hash, data['current_password']):
            return jsonify({"error": "Current password is incorrect"}), 400
        user.password_hash = generate_password_hash(data['password'])

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """Generate a reset token for the user."""
    data = request.get_json()
    if not data.get('email'):
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "No account found with that email"}), 404

    token = secrets.token_hex(32)
    reset_tokens[token] = user.id
    return jsonify({"message": "Reset token generated", "token": token}), 200


@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    """Reset password using a valid token."""
    data = request.get_json()
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400

    user_id = reset_tokens.get(token)
    if not user_id:
        return jsonify({"error": "Invalid or expired reset token"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password_hash = generate_password_hash(new_password)
    try:
        db.session.commit()
        del reset_tokens[token]
        return jsonify({"message": "Password reset successful"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@auth_bp.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Return all user accounts."""
    users = User.query.filter_by(is_admin=False).all()
    return jsonify([
        {
            "id": user.id,
            "student_id": user.student_id,
            "display_name": user.display_name,
            "email": user.email,
            "account_status": user.account_status,
            "is_admin": user.is_admin
        }
        for user in users
    ]), 200


@auth_bp.route('/login')
def login_page():
    """Render the login page."""
    return render_template('login.html')


@auth_bp.route('/register')
def register_page():
    """Render the register page."""
    return render_template('register.html')


@auth_bp.route('/profile')
@login_required_redirect
def profile_page():
    """Render the profile page."""
    return render_template('profile.html')


@auth_bp.route('/forgot-password')
def forgot_password_page():
    """Render the forgot password page."""
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password')
def reset_password_page():
    """Render the reset password page."""
    return render_template('reset_password.html')


@auth_bp.route('/logout')
def logout_page():
    """Logout the current user and redirect to login."""
    session.clear()
    return redirect('/login')


@auth_bp.route('/admin/login')
def admin_login_page():
    """Render the admin login page."""
    return render_template('admin_login.html')


@auth_bp.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Administrator login."""
    data = request.get_json()

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if user.account_status == "suspended":
        return jsonify({
            "error": "Your account has been suspended"
        }), 403

    if not user.is_admin:
        return jsonify({
            "error": "This account is not an administrator account."
        }), 403

    session.permanent = True
    session["user_id"] = user.id

    return jsonify({
        "message": "Administrator login successful",
        "user_id": user.id
    }), 200


@auth_bp.route('/admin/logout')
def admin_logout():
    """Logout administrator."""
    session.clear()
    return redirect('/admin/login')
