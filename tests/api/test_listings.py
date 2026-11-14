"""API tests for SwapLah listings endpoints."""
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    """Setup temporary in-memory database and test client with logged-in user."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:' 
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Create mock user for authenticated requests
            user = User(id=1, student_id="1", first_name="A", last_name="B", 
                        display_name="Irsyad", email="a@nyp.edu.sg", 
                        contact_number="1", password_hash="hash", account_status="active")
            db.session.add(user)
            db.session.commit()
            
            with client.session_transaction() as sess:
                sess['user_id'] = 1
        yield client

def test_health_api(client):
    """Test health check API endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

def test_get_listings_api(client):
    """Test the GET /api/listings API endpoint (Positive)."""
    response = client.get('/api/listings')
    assert response.status_code == 200
    assert 'listings' in response.json

def test_create_listing_api_success(client):
    """Test POST /api/listings endpoint (Positive)."""
    payload = {
        "title": "API Test Item",
        "description": "Testing API creation",
        "price": "20.00",
        "category": "Electronics",
        "condition": "New",
        "image_url": "http://test.com/api.jpg"
    }
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 201
    assert response.json['title'] == "API Test Item"

def test_create_listing_api_missing_fields(client):
    """Test POST /api/listings endpoint with missing data (Negative)."""
    response = client.post('/api/listings', json={"title": "Incomplete"})
    assert response.status_code == 400
    assert 'error' in response.json

def test_update_listing_api(client):
    """Test PUT /api/listings/<id> endpoint."""
    # Create an item first
    post_res = client.post('/api/listings', json={
        "title": "Old Title", "description": "d", "price": "10",
        "category": "Books", "condition": "Good", "image_url": "t.jpg"
    })
    listing_id = post_res.json['id']

    # Update it via API
    put_res = client.put(f'/api/listings/{listing_id}', json={"title": "Updated API Title"})
    assert put_res.status_code == 200
    assert put_res.json['title'] == "Updated API Title"

def test_delete_listing_api(client):
    """Test DELETE /api/listings/<id> endpoint."""
    post_res = client.post('/api/listings', json={
        "title": "To Delete", "description": "d", "price": "10",
        "category": "Books", "condition": "Good", "image_url": "t.jpg"
    })
    listing_id = post_res.json['id']

    del_res = client.delete(f'/api/listings/{listing_id}')
    assert del_res.status_code == 200

def test_get_listing_detail_404(client):
    """Test GET /api/listings/<id> with non-existent ID (Negative)."""
    response = client.get('/api/listings/does-not-exist')
    assert response.status_code == 404
