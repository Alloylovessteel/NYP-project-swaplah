"""Entry point for the SwapLah Flask application.""" # File docstring
from flask import Flask, jsonify

def create_app():
    """Create and configure the Flask app.""" # Function docstring
    app = Flask(__name__)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify server is running."""
        return jsonify({"status": "ok"}), 200

    return app