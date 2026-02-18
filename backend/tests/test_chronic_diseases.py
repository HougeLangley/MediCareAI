import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, ChronicDisease, PatientChronicCondition


class TestChronicDiseases:
    """Tests for chronic disease endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_chronic_diseases(
        self, 
        client: AsyncClient, 
        test_chronic_disease: ChronicDisease
    ):
        """Test listing all chronic diseases."""
        response = await client.get("/api/v1/chronic-diseases")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
        assert data["items"][0]["icd10_code"] == "E11"
    
    @pytest.mark.asyncio
    async def test_get_chronic_disease_detail(
        self, 
        client: AsyncClient, 
        test_chronic_disease: ChronicDisease
    ):
        """Test getting a specific chronic disease."""
        response = await client.get(f"/api/v1/chronic-diseases/{test_chronic_disease.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["icd10_code"] == "E11"
        assert data["icd10_name"] == "Type 2 diabetes mellitus"
    
    @pytest.mark.asyncio
    async def test_add_chronic_disease_to_patient(
        self, 
        client: AsyncClient, 
        test_user: User,
        test_chronic_disease: ChronicDisease,
        db_session: AsyncSession
    ):
        """Test adding a chronic disease to patient profile."""
        # Login first
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Add chronic disease
        response = await client.post(
            "/api/v1/patients/me/chronic-diseases",
            json={
                "disease_id": str(test_chronic_disease.id),
                "severity": "moderate",
                "notes": "Test notes"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["disease_id"] == str(test_chronic_disease.id)
        assert data["severity"] == "moderate"
    
    @pytest.mark.asyncio
    async def test_list_patient_chronic_diseases(
        self,
        client: AsyncClient,
        test_user: User,
        test_chronic_disease: ChronicDisease,
        db_session: AsyncSession
    ):
        """Test listing patient's chronic diseases."""
        # Create a patient condition
        condition = PatientChronicCondition(
            patient_id=test_user.id,
            disease_id=test_chronic_disease.id,
            severity="mild",
            is_active=True
        )
        db_session.add(condition)
        await db_session.commit()
        
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        token = login_response.json()["access_token"]
        
        # Get patient's diseases
        response = await client.get(
            "/api/v1/patients/me/chronic-diseases",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1


class TestAuth:
    """Tests for authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient):
        """Test user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert "id" in data
    
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
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
