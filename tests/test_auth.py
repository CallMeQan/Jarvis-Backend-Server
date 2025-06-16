import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User, ForgotPassword
from flask_jwt_extended import decode_token

@pytest.fixture
def app():
    config_override = {
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'jwt-test-secret-key',
        'MAIL_SERVER': 'localhost',
        'MAIL_PORT': 8025,
        'MAIL_DEFAULT_SENDER': 'test@example.com',
        'MAIL_SUPPRESS_SEND': True
    }
    app = create_app('testing', config_override=config_override)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

# Test register
def test_register(client):
    data = {
        "username": "testuser",
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "retype_password": "password123"
    }
    response = client.post("/auth/register", json=data)
    assert response.status_code == 201
    assert "access_token" in response.get_json()

# Test login
def test_login(client):
    client.post("/auth/register", json={
        "username": "testlogin",
        "name": "Test Login",
        "email": "login@example.com",
        "password": "password123",
        "retype_password": "password123"
    })
    user = User.query.filter_by(email="login@example.com").first()
    user.is_verified = True
    _db.session.commit()
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

# Test profile (requires JWT)
def test_profile(client):
    client.post("/auth/register", json={
        "username": "testprofile",
        "name": "Test Profile",
        "email": "profile@example.com",
        "password": "password123",
        "retype_password": "password123"
    })
    user = User.query.filter_by(email="profile@example.com").first()
    user.is_verified = True
    _db.session.commit()
    login_resp = client.post("/auth/login", json={
        "email": "profile@example.com",
        "password": "password123"
    })
    token = login_resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/profile", headers=headers)
    if response.status_code != 200:
        print("/auth/profile response:", response.get_json())
    assert response.status_code == 200
    assert response.get_json()["email"] == "profile@example.com"

# Test forgot_password
def test_forgot_password(client):
    client.post("/auth/register", json={
        "username": "testforgot",
        "name": "Test Forgot",
        "email": "forgot@example.com",
        "password": "password123",
        "retype_password": "password123"
    })
    user = User.query.filter_by(email="forgot@example.com").first()
    user.is_verified = True
    _db.session.commit()
    response = client.post("/auth/forgot-password", json={"email": "forgot@example.com"})
    assert response.status_code == 200
    assert "Reset link sent" in response.get_json()["msg"]

# Test logout
def test_logout(client):
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert "Logout successful" in response.get_json()["msg"]

# Print 'all success' if all tests pass
def pytest_sessionfinish(session, exitstatus):
    if exitstatus == 0:
        print("all success")
