# MediCareAI Backend Tests

This directory contains automated tests for the MediCareAI backend API.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_chronic_diseases.py # Chronic disease endpoint tests
└── README.md                # This file
```

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
cd backend
pip install -r requirements-test.txt
```

2. Ensure you have a test database available or use the main database with test data.

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_chronic_diseases.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## Test Categories

### Unit Tests
- Model validation
- Service logic
- Utility functions

### Integration Tests
- API endpoint testing
- Database operations
- Authentication flow

### Test Data

Tests use fixtures defined in `conftest.py`:
- `test_user` - Standard patient user
- `test_doctor` - Verified doctor user
- `test_chronic_disease` - Sample chronic disease

## Adding New Tests

1. Create test file: `test_<feature>.py`
2. Use existing fixtures or create new ones in `conftest.py`
3. Follow naming convention: `test_<description>`
4. Use type hints for better IDE support

## Best Practices

- Use async/await for all database operations
- Clean up test data after each test
- Mock external services (AI API, OSS, etc.)
- Test both success and error cases
