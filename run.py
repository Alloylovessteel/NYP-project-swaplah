"""Script to run the Flask development server."""
from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True allows the server to auto-reload when you change code
    app.run(debug=True, port=5000)