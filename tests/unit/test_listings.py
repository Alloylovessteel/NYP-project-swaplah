"""Unit tests for Listing management (Creation, Search, Filter, Pagination)."""
import pytest
from app import create_app, db
from app.models import Listing

@pytest.fixture
def client():
    """Setup a temporary database and test client."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

# --- CREATION TESTS (TC01, TC02) ---
def test_create_listing_success(client):
    payload = {"title": "Physics Book", "description": "d", "price": "10",
               "category": "Books", "condition": "New", "image_url": "t.jpg"}
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 201

def test_create_listing_missing_field(client):
    response = client.post('/api/listings', json={"title": "Incomplete"})
    assert response.status_code == 400

# --- SEARCH & FILTER TESTS (TC03, TC04, TC10) ---
def test_get_listings_search(client):
    client.post('/api/listings', json={"title": "Physics Book", "description": "d", "price": "10",
                                       "category": "Books", "condition": "Good", "image_url": "t.jpg"})
    response = client.get('/api/listings?search=Physics')
    assert response.status_code == 200
    assert len(response.json['listings']) == 1

def test_get_listings_filter_category(client):
    client.post('/api/listings', json={"title": "Calc", "description": "d", "price": "5",
                                       "category": "Electronics", "condition": "New", "image_url": "t.jpg"})
    response = client.get('/api/listings?category=Electronics')
    assert response.json['listings'][0]['category'] == "Electronics"

def test_search_no_results(client):
    response = client.get('/api/listings?search=NonExistentItem')
    assert response.status_code == 200
    assert len(response.json['listings']) == 0

# --- PAGINATION TESTS (TC05, TC06) ---
def test_pagination_logic(client):
    for i in range(12):
        client.post('/api/listings', json={"title": f"Item {i}", "description": "d", "price": "1",
                                           "category": "Test", "condition": "New", "image_url": "t.jpg"})
    response = client.get('/api/listings?page=1')
    assert len(response.json['listings']) == 10
    response2 = client.get('/api/listings?page=2')
    assert len(response2.json['listings']) == 2

# --- EDIT & DELETE TESTS (TC07, TC08, TC09) ---
def test_update_listing(client):
    res = client.post('/api/listings', json={"title": "Old", "description": "d", "price": "1",
                                             "category": "C", "condition": "N", "image_url": "t.jpg"})
    l_id = res.json['id']
    upd = client.put(f'/api/listings/{l_id}', json={"title": "New"})
    assert upd.status_code == 200
    assert upd.json['title'] == "New"

def test_soft_delete_listing(client):
    res = client.post('/api/listings', json={"title": "Del", "description": "d", "price": "1",
                                             "category": "C", "condition": "N", "image_url": "t.jpg"})
    l_id = res.json['id']
    client.delete(f'/api/listings/{l_id}')
    assert len(client.get('/api/listings').json['listings']) == 0

def test_edit_nonexistent_listing(client):
    response = client.put('/api/listings/invalid-id', json={"title": "New"})
    assert response.status_code == 404
