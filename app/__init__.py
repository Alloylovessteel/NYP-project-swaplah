"""Entry point for the SwapLah Flask application."""
from flask import Flask, jsonify
from .models import db

def create_app(test_config=None):
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swaplah.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes import listings_bp
    from .auth import auth_bp
    from .review_routes import review_bp
    app.register_blueprint(listings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(review_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify server is running."""
        return jsonify({"status": "ok"}), 200

    return app