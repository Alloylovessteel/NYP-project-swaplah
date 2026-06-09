"""Unit tests for Listing creation."""
import pytest
from app import create_app, db
from app.models import Listing

@pytest.fixture
def client():
    """Setup a temporary database and test client."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Use a temporary in-memory DB
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_listing_success(client):
    """Test that a valid listing is created successfully (Positive Case)."""
    payload = {
        "title": "Test Item",
        "description": "A test description",
        "price": "10.00",
        "category": "Electronics",
        "condition": "New",
        "image_url": "http://test.com/img.jpg"
    }
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 201
    assert response.json['title'] == "Test Item"

def test_create_listing_missing_field(client):
    """Test that missing fields return a 400 error (Negative Case)."""
    payload = {"title": "Incomplete Item"} # Missing price, desc, etc.
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 400
    assert "error" in response.json