"""Unit tests for Listing management (Creation, Search, Filter, Pagination)."""
import pytest
from app import create_app, db
from app.models import Listing

@pytest.fixture
def client():
    """Setup a temporary database and test client."""
    # Pass the test configuration to the app factory
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

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
    payload = {"title": "Incomplete Item"}
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 400
    assert "error" in response.json

def test_get_listings_search(client):
    """Test searching for an item by keyword in Title or Description."""
    # Create a test item
    client.post('/api/listings', json={
        "title": "Physics Book", "description": "Used for Year 1", "price": "10",
        "category": "Books", "condition": "Good", "image_url": "test.jpg"
    })

    # Search for 'Physics'
    response = client.get('/api/listings?search=Physics')
    assert response.status_code == 200
    assert len(response.json['listings']) == 1
    assert "Physics" in response.json['listings'][0]['title']

def test_get_listings_filter_category(client):
    """Test filtering results by Category."""
    client.post('/api/listings', json={
        "title": "Calculator", "description": "Casio", "price": "15",
        "category": "Electronics", "condition": "New", "image_url": "t.jpg"
    })
    client.post('/api/listings', json={
        "title": "Shirt", "description": "NYP Shirt", "price": "5",
        "category": "Clothing", "condition": "New", "image_url": "t.jpg"
    })

    # Filter by 'Electronics'
    response = client.get('/api/listings?category=Electronics')
    assert len(response.json['listings']) == 1
    assert response.json['listings'][0]['category'] == "Electronics"

# --- PAGINATION TEST ---

def test_pagination_logic(client):
    """Test that the API only returns 10 items per page (Requirement C.vi)."""
    # Create 12 dummy items
    for i in range(12):
        client.post('/api/listings', json={
            "title": f"Item {i}", "description": "desc", "price": "5",
            "category": "Test", "condition": "New", "image_url": "t.jpg"
        })

    # Check page 1 (Should have 10 items)
    response = client.get('/api/listings?page=1')
    assert len(response.json['listings']) == 10
    assert response.json['total'] == 12
    assert response.json['pages'] == 2

    # Check page 2 (Should have the remaining 2 items)
    response = client.get('/api/listings?page=2')
    assert len(response.json['listings']) == 2
