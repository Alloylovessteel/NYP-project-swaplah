"""Entry point for the SwapLah Flask application."""
from flask import Flask, jsonify
from .models import db

def create_app(test_config=None): # Added test_config parameter
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swaplah.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        # Only create tables if they don't exist
        db.create_all()

    from .routes import listings_bp
    app.register_blueprint(listings_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify server is running."""
        return jsonify({"status": "ok"}), 200

    return app
