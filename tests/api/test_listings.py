import pytest
from app import create_app, db
from app.models import Listing

@pytest.fixture
def client():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:' 
    })

    with app.test_client() as client:
        with app.app_context():
            db.create_all() 
        yield client

def test_health_api(client):
    """Test health check API."""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'

def test_listings_get_api(client):
    """Test the GET /api/listings API endpoint."""
    response = client.get('/api/listings')
    assert response.status_code == 200
    assert 'listings' in response.json

def test_get_listing_detail_404(client):
    response = client.get('/api/listings/does-not-exist')
    assert response.status_code == 404
