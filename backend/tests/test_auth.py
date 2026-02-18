import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User
from app.core.security import get_password_hash


class TestAuthEndpoints:
    """Comprehensive tests for authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_patient_success(self, client: AsyncClient):
        """Test successful patient registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newpatient@example.com",
                "password": "password123",
                "full_name": "New Patient",
                "role": "patient"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newpatient@example.com"
        assert data["full_name"] == "New Patient"
        assert data["role"] == "patient"
        assert "id" in data
        assert "password_hash" not in data  # Should not return password
    
    @pytest.mark.asyncio
    async def test_register_doctor_success(self, client: AsyncClient):
        """Test successful doctor registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newdoctor@example.com",
                "password": "password123",
                "full_name": "New Doctor",
                "role": "doctor",
                "license_number": "DOC987654",
                "hospital": "Test Hospital",
                "specialty": "Cardiology"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newdoctor@example.com"
        assert data["role"] == "doctor"
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self, 
        client: AsyncClient, 
        test_user: User
    ):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",  # Already exists
                "password": "password123",
                "full_name": "Duplicate User"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.text.lower() or "already registered" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "password": "password123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",  # Too short
                "full_name": "Test User"
            }
        )
        
        assert response.status_code in [400, 422]  # Bad request or validation error
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "test123456"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data or "email" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient, test_user: User):
        """Test retrieving current user info."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        token = login_response.json()["access_token"]
        
        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_auth(self, client: AsyncClient):
        """Test retrieving current user without authentication."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_update_user_profile(self, client: AsyncClient, test_user: User):
        """Test updating user profile."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        token = login_response.json()["access_token"]
        
        # Update profile
        response = await client.put(
            "/api/v1/auth/me",
            json={
                "full_name": "Updated Name",
                "phone": "13800138000"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["phone"] == "13800138000"
    
    @pytest.mark.asyncio
    async def test_logout(self, client: AsyncClient, test_user: User):
        """Test logout functionality."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        token = login_response.json()["access_token"]
        refresh_token = login_response.json()["refresh_token"]
        
        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test token refresh."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data


class TestAuthValidation:
    """Tests for authentication input validation."""
    
    @pytest.mark.asyncio
    async def test_login_missing_email(self, client: AsyncClient):
        """Test login without email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"password": "password123"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_login_missing_password(self, client: AsyncClient):
        """Test login without password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_missing_required_fields(self, client: AsyncClient):
        """Test registration without required fields."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"}  # Missing password and full_name
        )
        
        assert response.status_code == 422
