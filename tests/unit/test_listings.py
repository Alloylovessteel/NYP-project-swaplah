"""Unit tests for Listing management (Creation, Search, Filter, Pagination)."""
import pytest
from app import create_app, db
from app.models import Listing, User

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
            user = User(id=1, student_id="1", first_name="A", last_name="B", 
                        display_name="Irsyad", email="a@nyp.edu.sg", 
                        contact_number="1", password_hash="hash", account_status="active")
            db.session.add(user)
            db.session.commit()
            with client.session_transaction() as sess:
                sess['user_id'] = 1
            yield client
            db.drop_all()

# --- CREATION TESTS (TC-LS-001, TC-LS-002) ---
def test_create_listing_success(client):
    payload = {"title": "Physics Book", "description": "d", "price": "10",
               "category": "Books", "condition": "New", "image_url": "t.jpg"}
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 201

def test_create_listing_missing_field(client):
    response = client.post('/api/listings', json={"title": "Incomplete"})
    assert response.status_code == 400

# --- SEARCH & FILTER TESTS (TC-LS-003, TC-LS-004, TC-LS-010) ---
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

# --- PAGINATION TESTS (TC-LS-005, TC-LS-006) ---
def test_pagination_logic(client):
    for i in range(12):
        client.post('/api/listings', json={"title": f"Item {i}", "description": "d", "price": "1",
                                           "category": "Test", "condition": "New", "image_url": "t.jpg"})
    response = client.get('/api/listings?page=1')
    assert len(response.json['listings']) == 10
    response2 = client.get('/api/listings?page=2')
    assert len(response2.json['listings']) == 2

# --- EDIT & DELETE TESTS (TC-LS-007, TC-LS-008, TC-LS-009) ---
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

# --- SECURITY TESTS (TC-SEC-002) ---
def test_unauthorized_edit(client):
    with client.application.app_context():
        listing = Listing(title="Owner Item", description="d", price="1", 
                          category="C", condition="N", image_url="t.jpg", seller_id=99)
        db.session.add(listing)
        db.session.commit()
        listing_id = listing.id

    response = client.put(f'/api/listings/{listing_id}', json={"title": "Hacked"})
    assert response.status_code == 403

# --- DETAIL VIEW TESTS ---
def test_get_listing_detail(client):
    """Test fetching a listing's detail view, including seller info."""
    res = client.post('/api/listings', json={
        "title": "Detail View Item", "description": "d", "price": "10",
        "category": "C", "condition": "N", "image_url": "t.jpg"
    })
    listing_id = res.json['id']

    response = client.get(f'/api/listings/{listing_id}')

    assert response.status_code == 200
    assert response.json['title'] == "Detail View Item"
    assert 'seller_info' in response.json
    assert response.json['seller_info']['display_name'] == "Irsyad"

def test_create_listing_invalid_price(client):
    payload = {
        "title": "Bad Price Item", 
        "description": "d", 
        "price": "asdfgh", #
        "category": "Books", 
        "condition": "New", 
        "image_url": "t.jpg"
    }
    response = client.post('/api/listings', json=payload)
    assert response.status_code == 400
    assert "Price must be a valid number" in response.json['error']

