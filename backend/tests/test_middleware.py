"""
Tests for authentication middleware and dependencies.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token
from datetime import timedelta

client = TestClient(app)


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # HTTPBearer auto_error


def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code == 401


def test_protected_endpoint_with_expired_token():
    """Test accessing protected endpoint with expired token"""
    # Create expired token
    expired_token = create_access_token(
        data={"sub": "999"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


def test_protected_endpoint_with_valid_token():
    """Test accessing protected endpoint with valid token"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "middleware@example.com",
            "password": "testpass123",
            "full_name": "Middleware Test"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "middleware@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "middleware@example.com"


def test_token_refresh():
    """Test token refresh endpoint"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "refresh@example.com",
            "password": "testpass123",
            "full_name": "Refresh Test"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "testpass123"
        }
    )
    old_token = login_response.json()["access_token"]
    
    # Refresh token
    refresh_response = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {old_token}"}
    )
    assert refresh_response.status_code == 200
    new_token = refresh_response.json()["access_token"]
    assert new_token != old_token
    
    # Verify new token works
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {new_token}"}
    )
    assert response.status_code == 200


def test_premium_access_non_premium_user():
    """Test premium endpoint with non-premium user"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "email": "nonpremium@example.com",
            "password": "testpass123",
            "full_name": "Non Premium"
        }
    )
    
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "nonpremium@example.com",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Try to access premium endpoint (assuming /api/premium/upgrade requires auth)
    # This is a placeholder - actual premium endpoints would be tested here
    response = client.get(
        "/api/auth/me",  # Using /me as example
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_premium"] == False


def test_malformed_authorization_header():
    """Test with malformed authorization header"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "InvalidFormat"}
    )
    assert response.status_code in [401, 403]


def test_missing_bearer_prefix():
    """Test with missing Bearer prefix"""
    token = create_access_token(data={"sub": "123"})
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": token}  # Missing "Bearer " prefix
    )
    assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
