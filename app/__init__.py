"""Entry point for the SwapLah Flask application."""
from flask import Flask, jsonify, redirect

from .models import db
from .auth import auth_bp
from .review_routes import review_bp
from .offers_routes import offers_bp
from .transactions_routes import transactions_bp
from .routes import listings_bp


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="dev-secret-key",
        SQLALCHEMY_DATABASE_URI="sqlite:///swaplah.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        PERMANENT_SESSION_LIFETIME=1800,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    app.register_blueprint(listings_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(offers_bp)
    app.register_blueprint(transactions_bp)

    with app.app_context():
        db.create_all()

    @app.after_request
    def set_security_headers(response):
        """Add security headers to every response."""
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Return a simple health status for the running app."""
        return jsonify({"status": "ok"}), 200

    @app.route("/")
    def home():
        """Send visitors to the marketplace."""
        return redirect("/marketplace")

    return app
