"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base, engine
from sqlalchemy.orm import Session

client = TestClient(app)


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "full_name": "Test User",
            "country": "India"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["country"] == "India"
    assert data["is_premium"] == False
    assert "id" in data


def test_register_duplicate_email():
    """Test registration with duplicate email"""
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    
    # Duplicate registration
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "testpass123",
            "full_name": "Test User 2"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_email():
    """Test registration with invalid email"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "invalid-email",
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 422  # Validation error


def test_register_short_password():
    """Test registration with short password"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test2@example.com",
            "password": "123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 422  # Validation error


def test_login_success():
    """Test successful login"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "testpass123",
            "full_name": "Login User"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    """Test login with wrong password"""
    # Register user first
    client.post(
        "/api/auth/register",
        json={
            "email": "wrongpass@example.com",
            "password": "correctpass",
            "full_name": "Test User"
        }
    )
    
    # Login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_nonexistent_user():
    """Test login with non-existent user"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 401


def test_get_current_user():
    """Test getting current user info"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "current@example.com",
            "password": "testpass123",
            "full_name": "Current User"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "current@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
    assert data["full_name"] == "Current User"


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
