import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app({'TESTING': True})
    with app.test_client() as client:
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

