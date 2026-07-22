"""Routes for user account management."""
import re
from flask import Blueprint, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User

auth_bp = Blueprint('auth', __name__)


def is_nyp_email(email):
    """Check if email is a valid NYP email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@(nyp\.edu\.sg|mymail\.nyp\.edu\.sg)$'
    return re.match(pattern, email) is not None


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

    if user.account_status == 'suspended':
        return jsonify({"error": "Your account has been suspended"}), 403

    session.permanent = True
    session['user_id'] = user.id
    return jsonify({"message": "Login successful", "user_id": user.id}), 200


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
        user.password_hash = generate_password_hash(data['password'])

    try:
        db.session.commit()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@auth_bp.route('/api/admin/users', methods=['GET'])
def get_users():
    """Return all user accounts."""
    users = User.query.all()
    return jsonify([
        {
            "id": user.id,
            "student_id": user.student_id,
            "display_name": user.display_name,
            "email": user.email,
            "account_status": user.account_status
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
def profile_page():
    """Render the profile page."""
    return render_template('profile.html')