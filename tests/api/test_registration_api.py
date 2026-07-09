"""API tests for POST /api/register (issue #50)."""
import pytest

from app import create_app
from app.models import db


@pytest.fixture
def client():
    test_config = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
    }
    app = create_app(test_config)
    with app.test_client() as test_client:
        yield test_client
    with app.app_context():
        db.session.remove()
        db.drop_all()


def make_payload(**overrides):
    payload = {
        'student_id': 'S2000001',
        'first_name': 'Amy',
        'last_name': 'Lee',
        'display_name': 'Amy L',
        'email': 'amy.lee@nyp.edu.sg',
        'contact_number': '98765432',
        'password': 'Pass1234!',
    }
    payload.update(overrides)
    return payload


# --- Positive cases ---

def test_register_success_returns_201(client):
    resp = client.post('/api/register', json=make_payload())
    assert resp.status_code == 201
    assert resp.get_json()['message'] == 'Registration successful'


def test_register_accepts_mymail_subdomain(client):
    resp = client.post('/api/register', json=make_payload(
        student_id='S2000003', email='bob@mymail.nyp.edu.sg'
    ))
    assert resp.status_code == 201


# --- Negative cases ---

def test_register_rejects_non_nyp_email(client):
    resp = client.post(
        '/api/register', json=make_payload(email='amy.lee@gmail.com')
    )
    assert resp.status_code == 400
    assert 'NYP' in resp.get_json()['error']


def test_register_rejects_missing_required_field(client):
    payload = make_payload()
    del payload['contact_number']
    resp = client.post('/api/register', json=payload)
    assert resp.status_code == 400
    assert 'contact_number' in resp.get_json()['error']


def test_register_rejects_blank_required_field(client):
    resp = client.post('/api/register', json=make_payload(first_name='   '))
    assert resp.status_code == 400


def test_register_rejects_duplicate_email(client):
    client.post('/api/register', json=make_payload())
    resp = client.post(
        '/api/register', json=make_payload(student_id='S2000002')
    )
    assert resp.status_code == 400
    assert 'Email' in resp.get_json()['error']


def test_register_rejects_duplicate_student_id(client):
    client.post('/api/register', json=make_payload())
    resp = client.post(
        '/api/register', json=make_payload(email='different@nyp.edu.sg')
    )
    assert resp.status_code == 400
    assert 'Student ID' in resp.get_json()['error']


def test_register_rejects_empty_body(client):
    resp = client.post('/api/register', json={})
    assert resp.status_code == 400
