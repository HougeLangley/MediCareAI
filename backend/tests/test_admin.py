import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User


class TestAdminEndpoints:
    """Tests for admin-specific endpoints."""
    
    @pytest.fixture
    async def test_admin(self, db_session: AsyncSession) -> User:
        """Create a test admin user."""
        from app.core.security import get_password_hash
        admin = User(
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            full_name="Test Admin",
            role="admin",
            is_active=True
        )
        db_session.add(admin)
        await db_session.commit()
        await db_session.refresh(admin)
        return admin
    
    @pytest.mark.asyncio
    async def test_admin_login(
        self, 
        client: AsyncClient,
        test_admin: User
    ):
        """Test admin login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "admin"
    
    @pytest.mark.asyncio
    async def test_admin_get_dashboard_stats(
        self,
        client: AsyncClient,
        test_admin: User
    ):
        """Test admin retrieving dashboard statistics."""
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get dashboard stats
        response = await client.get(
            "/api/v1/admin/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Check expected fields
        assert "user_count" in data or "total_users" in data
    
    @pytest.mark.asyncio
    async def test_admin_list_doctors(
        self,
        client: AsyncClient,
        test_admin: User,
        test_doctor: User
    ):
        """Test admin listing pending doctor verifications."""
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get pending doctors
        response = await client.get(
            "/api/v1/admin/doctors?status=pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        doctors = response.json()
        assert isinstance(doctors, list)
    
    @pytest.mark.asyncio
    async def test_admin_get_system_metrics(
        self,
        client: AsyncClient,
        test_admin: User
    ):
        """Test admin retrieving system metrics."""
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get system metrics
        response = await client.get(
            "/api/v1/admin/system/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should contain CPU, memory, disk metrics
        assert any(key in data for key in ["cpu", "memory", "disk", "cpu_usage", "memory_usage"])
    
    @pytest.mark.asyncio
    async def test_admin_get_audit_logs(
        self,
        client: AsyncClient,
        test_admin: User
    ):
        """Test admin retrieving audit logs."""
        # Login as admin
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Get audit logs
        response = await client.get(
            "/api/v1/admin/audit-logs?limit=10",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        logs = response.json()
        assert isinstance(logs, list)


class TestAdminUnauthorized:
    """Tests for unauthorized admin access."""
    
    @pytest.mark.asyncio
    async def test_doctor_cannot_access_admin_endpoints(
        self,
        client: AsyncClient,
        test_doctor: User
    ):
        """Test that doctors cannot access admin endpoints."""
        # Login as doctor
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "doctor123"}
        )
        token = login_response.json()["access_token"]
        
        # Try to access admin dashboard
        response = await client.get(
            "/api/v1/admin/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_patient_cannot_access_admin_endpoints(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test that patients cannot access admin endpoints."""
        # Login as patient
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        token = login_response.json()["access_token"]
        
        # Try to access admin endpoints
        response = await client.get(
            "/api/v1/admin/system/metrics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_admin_endpoints_require_auth(self, client: AsyncClient):
        """Test that admin endpoints require authentication."""
        endpoints = [
            "/api/v1/admin/dashboard/stats",
            "/api/v1/admin/doctors",
            "/api/v1/admin/system/metrics",
            "/api/v1/admin/audit-logs"
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401, f"Endpoint {endpoint} should require auth"
