import pytest
from werkzeug.security import generate_password_hash
from models import User


def test_login_logout_flow(client, db, app):
    # Create a test user in the test database
    with app.app_context():
        user = User(username='testuser', password=generate_password_hash('testpass'), role='admin')
        db.session.add(user)
        db.session.commit()
    # Test login with correct credentials
    resp = client.post('/login', data={'username': 'testuser', 'password': 'testpass'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Logged in successfully' in resp.data
    # Test logout
    resp = client.get('/logout', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Logged out successfully' in resp.data


def test_login_invalid_credentials(client):
    # Attempt login with invalid credentials
    resp = client.post('/login', data={'username': 'invalid', 'password': 'wrong'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Invalid username or password' in resp.data
