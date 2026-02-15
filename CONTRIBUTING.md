# Contributing to MediCareAI

First off, thank you for considering contributing to MediCareAI! It's people like you that make MediCareAI such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to see if the problem has already been reported. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and what behavior you expected**
- **Include screenshots if possible**
- **Include your environment details** (OS, Docker version, browser, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the enhancement**
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repository
2. Create a new branch from `main` for your feature or bug fix
3. Make your changes
4. Run tests and ensure they pass
5. Update documentation if needed
6. Submit a pull request

## Development Setup

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/MediCareAI.git
cd MediCareAI
```

2. **Create a branch for your changes**
```bash
git checkout -b feature/your-feature-name
```

3. **Start the development environment**
```bash
cp .env.example .env
# Edit .env with your configuration
./scripts/deploy.sh
```

4. **Make your changes**

5. **Test your changes**
```bash
# Run backend tests
docker-compose exec backend pytest

# Test API endpoints
curl http://localhost:8000/health
```

6. **Commit your changes**
```bash
git add .
git commit -m "Add feature: description of your changes"
```

7. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

8. **Create a Pull Request**

## Style Guidelines

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Example:
```
Add patient search functionality

- Implement search by name and MRN
- Add fuzzy matching for name searches
- Update API documentation
- Add unit tests

Fixes #123
```

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 100 characters maximum
- **Imports**: Group imports in this order:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Use type hints for function parameters and return values

Example:
```python
from typing import Optional
from fastapi import HTTPException

from app.models.models import User


def get_user_by_email(email: str) -> Optional[User]:
    """Retrieve a user by their email address.
    
    Args:
        email: The email address to search for.
        
    Returns:
        The user if found, None otherwise.
        
    Raises:
        HTTPException: If the database query fails.
    """
    # Implementation here
    pass
```

### JavaScript Code Style

- Use 2 spaces for indentation
- Use semicolons
- Use single quotes for strings
- Use camelCase for variables and functions
- Use PascalCase for classes
- Add JSDoc comments for functions

Example:
```javascript
/**
 * Fetches patient data from the API
 * @param {string} patientId - The patient ID
 * @returns {Promise<Object>} The patient data
 */
async function fetchPatientData(patientId) {
  const response = await fetch(`/api/v1/patients/${patientId}`, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  });
  return response.json();
}
```

### Database Migrations

When making changes to database models:

1. Update the model in `backend/app/models/models.py`
2. Create a migration:
```bash
docker-compose exec backend alembic revision --autogenerate -m "Description of changes"
```
3. Review the generated migration
4. Apply the migration:
```bash
docker-compose exec backend alembic upgrade head
```

### Documentation

- Update the README.md if you change functionality
- Update API_REFERENCE.md for API changes
- Add docstrings to new functions and classes
- Update DEPLOYMENT.md if deployment process changes

## Testing

### Running Tests

```bash
# Backend tests
docker-compose exec backend pytest

# With coverage
docker-compose exec backend pytest --cov=app

# Specific test file
docker-compose exec backend pytest tests/test_patients.py
```

### Writing Tests

- Place tests in `backend/tests/`
- Name test files `test_*.py`
- Use pytest fixtures for database setup
- Mock external API calls

Example:
```python
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_patient():
    """Test creating a new patient."""
    response = client.post(
        "/api/v1/patients",
        json={
            "name": "Test Patient",
            "date_of_birth": "1990-01-01",
            "gender": "male"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Patient"
```

## Documentation

### Updating Documentation

Documentation is located in:
- `README.md` - Main project documentation
- `docs/` - Additional documentation
- `AGENTS.md` - AI assistant context
- Code docstrings

When adding features:
1. Update relevant documentation
2. Add API examples if adding endpoints
3. Update deployment docs if process changes

## Release Process

1. Update version number in relevant files
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release with semantic versioning (e.g., v1.2.3)

## Questions?

Feel free to:
- Open an issue for questions
- Join discussions in existing issues
- Contact maintainers

## Recognition

Contributors will be recognized in our README.md file and release notes.

Thank you for contributing to MediCare_AI! 🎉
