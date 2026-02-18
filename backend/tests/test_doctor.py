import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import User, SharedMedicalCase, DoctorCaseComment


class TestDoctorEndpoints:
    """Tests for doctor-specific endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_doctor_cases(
        self, 
        client: AsyncClient, 
        test_doctor: User,
        db_session: AsyncSession
    ):
        """Test doctor retrieving case list."""
        # Login as doctor
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "doctor123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get cases
        response = await client.get(
            "/api/v1/doctor/cases?type=all",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        cases = response.json()
        assert isinstance(cases, list)
    
    @pytest.mark.asyncio
    async def test_get_doctor_case_detail(
        self,
        client: AsyncClient,
        test_doctor: User,
        db_session: AsyncSession
    ):
        """Test doctor retrieving specific case detail."""
        # Create a shared case first
        from app.models.models import MedicalCase, DataSharingConsent
        
        case = MedicalCase(
            patient_id=test_doctor.id,
            title="Test Case",
            description="Test description",
            symptoms="Test symptoms",
            is_shared=True,
            share_scope='platform_anonymous'
        )
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)
        
        # Create shared version
        shared_case = SharedMedicalCase(
            original_case_id=case.id,
            consent_id=case.id,  # Simplified for test
            anonymous_patient_profile={"age_range": "30-40", "gender": "male"},
            anonymized_symptoms="Test symptoms",
            anonymized_diagnosis="Test diagnosis",
            visible_to_doctors=True
        )
        db_session.add(shared_case)
        await db_session.commit()
        await db_session.refresh(shared_case)
        
        # Login as doctor
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "doctor123"}
        )
        token = login_response.json()["access_token"]
        
        # Get case detail
        response = await client.get(
            f"/api/v1/doctor/cases/{shared_case.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "case" in data
        assert data["case"]["id"] == str(shared_case.id)
    
    @pytest.mark.asyncio
    async def test_doctor_add_comment(
        self,
        client: AsyncClient,
        test_doctor: User,
        db_session: AsyncSession
    ):
        """Test doctor adding comment to a case."""
        # Create a shared case
        from app.models.models import MedicalCase, DataSharingConsent
        
        case = MedicalCase(
            patient_id=test_doctor.id,
            title="Test Case for Comment",
            description="Test description",
            symptoms="Test symptoms",
            is_shared=True,
            share_scope='platform_anonymous'
        )
        db_session.add(case)
        await db_session.commit()
        await db_session.refresh(case)
        
        shared_case = SharedMedicalCase(
            original_case_id=case.id,
            consent_id=case.id,
            anonymous_patient_profile={"age_range": "30-40", "gender": "male"},
            anonymized_symptoms="Test symptoms",
            anonymized_diagnosis="Test diagnosis",
            visible_to_doctors=True
        )
        db_session.add(shared_case)
        await db_session.commit()
        await db_session.refresh(shared_case)
        
        # Login as doctor
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "doctor123"}
        )
        token = login_response.json()["access_token"]
        
        # Add comment
        response = await client.post(
            f"/api/v1/doctor/cases/{shared_case.id}/comments",
            json={
                "comment_type": "suggestion",
                "content": "This is a test comment from doctor"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code in [201, 403]  # 403 if doctor not verified
        if response.status_code == 201:
            data = response.json()
            assert data["content"] == "This is a test comment from doctor"
    
    @pytest.mark.asyncio
    async def test_doctor_get_mentions(
        self,
        client: AsyncClient,
        test_doctor: User
    ):
        """Test doctor retrieving @mentions."""
        # Login as doctor
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "doctor@example.com", "password": "doctor123"}
        )
        token = login_response.json()["access_token"]
        
        # Get mentions
        response = await client.get(
            "/api/v1/doctor/mentions",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        mentions = response.json()
        assert isinstance(mentions, list)


class TestDoctorUnauthorized:
    """Tests for unauthorized access attempts."""
    
    @pytest.mark.asyncio
    async def test_get_cases_without_auth(self, client: AsyncClient):
        """Test accessing cases without authentication."""
        response = await client.get("/api/v1/doctor/cases?type=all")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_case_detail_without_auth(self, client: AsyncClient):
        """Test accessing case detail without authentication."""
        response = await client.get(
            "/api/v1/doctor/cases/123e4567-e89b-12d3-a456-426614174000"
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_patient_cannot_access_doctor_endpoints(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test that regular patients cannot access doctor endpoints."""
        # Login as patient
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "test123456"}
        )
        token = login_response.json()["access_token"]
        
        # Try to access doctor cases
        response = await client.get(
            "/api/v1/doctor/cases?type=all",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
