"""Entry point for the SwapLah Flask application.""" # File docstring
import os
from flask import Flask, jsonify
from .models import db # Import the database object

def create_app():
    """Create and configure the Flask app.""" # Function docstring
    app = Flask(__name__)

    #Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swaplah.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all() # Creates the .db file automatically

    from .routes import listings_bp
    app.register_blueprint(listings_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify server is running."""
        return jsonify({"status": "ok"}), 200

    return app
