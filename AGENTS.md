# AGENTS.md - AI Assistant Project Context

This document provides context for AI assistants working on the MediCare_AI project.

## Project Overview

**MediCare_AI** is an intelligent disease management system with the following key characteristics:
- **Purpose**: AI-powered healthcare diagnosis and patient management
- **Architecture**: Full-stack web application with Docker containerization
- **AI Integration**: Uses GLM-4.7-Flash (local via llama.cpp) for diagnosis
- **Document Processing**: Integrates MinerU for medical document text extraction
- **Database**: PostgreSQL with SQLAlchemy async ORM
- **Frontend**: Vanilla HTML/CSS/JavaScript (not React as mentioned in old docs)

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│   Frontend   │ │   Backend   │ │    Redis    │
│  HTML/CSS/JS │ │   FastAPI   │ │    Cache    │
└──────────────┘ └──────┬──────┘ └─────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼────────┐
│  PostgreSQL  │ │    MinerU   │ │   GLM-4.7     │
│  Database    │ │     API     │ │    Flash      │
└──────────────┘ └─────────────┘ └───────────────┘
```

## Key Components

### 1. Backend (`/backend`)
- **Framework**: FastAPI with Python 3.11
- **Database**: PostgreSQL 15 with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT-based with refresh tokens
- **Main File**: `app/main.py`

#### Critical Files:
- `app/main.py` - Application entry point
- `app/models/models.py` - Database models (8 tables)
- `app/api/api_v1/api.py` - API router aggregation
- `app/core/security.py` - JWT and password hashing
- `app/services/ai_service.py` - AI diagnosis logic
- `app/services/mineru_service.py` - Document processing

#### API Structure:
```
/api/v1/auth/*           - Authentication endpoints
/api/v1/patients/*       - Patient CRUD
/api/v1/ai/*            - AI diagnosis
/api/v1/medical-cases/*  - Medical records
/api/v1/documents/*     - File upload/processing
```

### 2. Frontend (`/frontend`)
- **Type**: Static HTML/CSS/JavaScript
- **No Build Step**: Direct file serving
- **Styling**: Inline CSS with component-based styles

#### Pages:
- `index.html` - Homepage with navigation
- `login.html` / `register.html` - Authentication
- `user-profile.html` - Patient information management
- `symptom-submit.html` - AI diagnosis submission
- `medical-records.html` - View diagnosis history

#### Key Frontend Patterns:
- API calls use `fetch()` with JWT in Authorization header
- Token storage in `localStorage`
- Form validation before submission
- Modal-based confirmation dialogs

### 3. Database Models (`/backend/app/models/models.py`)

8 Core Tables:
1. **users** - User accounts with auth
2. **patients** - Patient profiles (linked to users)
3. **diseases** - Disease definitions and guidelines
4. **medical_cases** - Medical records/cases
5. **medical_documents** - Uploaded files with extracted content
6. **ai_feedbacks** - AI diagnosis results
7. **follow_ups** - Scheduled follow-ups
8. **user_sessions** - Active JWT sessions
9. **audit_logs** - Security audit trail

### 4. AI Service (`/backend/app/services/ai_service.py`)

**Key Function**: `comprehensive_diagnosis()`

Flow:
1. Collect patient personal info
2. Accept symptoms + optional file upload
3. Extract text from uploaded documents (MinerU)
4. Query knowledge base for relevant guidelines
5. Send to GLM-4.7-Flash AI model
6. Parse AI response
7. Save diagnosis to medical_records
8. Return structured diagnosis result

### 5. Knowledge Base (`/backend/data/knowledge_bases/`)

Structure:
```
knowledge_bases/
├── diseases/
│   └── respiratory/
│       ├── respiratory.json           # Disease metadata
│       └── *.md                       # Medical guidelines (Markdown)
├── active/
│   └── current.json                   # Active knowledge base config
```

## Development Workflow

### Adding a New Feature

1. **Database Changes**:
   - Update `app/models/models.py`
   - Create Alembic migration if needed
   - Update Pydantic schemas in `app/schemas/`

2. **Backend API**:
   - Add endpoint in `app/api/api_v1/endpoints/`
   - Register in `app/api/api_v1/api.py`
   - Add service logic in `app/services/`

3. **Frontend**:
   - Create/modify HTML page in `/frontend/`
   - Add API integration with proper error handling
   - Update navigation if needed

4. **Testing**:
   - Test API with curl or Postman
   - Test frontend integration
   - Verify database records

### Environment Setup

**Required Environment Variables** (see `.env.example`):
```bash
POSTGRES_PASSWORD=     # Database password
REDIS_PASSWORD=        # Redis password
JWT_SECRET_KEY=        # Min 32 characters
MINERU_TOKEN=          # MinerU API token
AI_API_KEY=            # AI model API key
AI_API_URL=            # AI endpoint (e.g., http://host:port/v1/)
AI_MODEL_ID=           # Model identifier
```

### Running Locally

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Database shell
docker-compose exec postgres psql -U medicare_user -d medicare_ai

# Backend shell
docker-compose exec backend bash
```

## Common Tasks

### Adding a New API Endpoint

1. Create function in appropriate endpoint file:
```python
@router.post("/new-endpoint")
async def new_endpoint(
    data: NewSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Implementation
    return result
```

2. Add Pydantic schema in `app/schemas/`
3. Test with: `curl -X POST http://localhost:8000/api/v1/...`

### Modifying Database Schema

1. Edit `app/models/models.py`
2. If using Alembic:
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "description"
   docker-compose exec backend alembic upgrade head
   ```
3. Or restart containers (data will be reset in dev)

### Debugging

**Backend Logs**:
```bash
docker-compose logs -f backend
```

**Database Query**:
```bash
docker-compose exec postgres psql -U medicare_user -d medicare_ai -c "SELECT * FROM users;"
```

**Test API**:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

## Important Notes

### Security
- NEVER commit `.env` file
- JWT tokens expire after 30 minutes (configurable)
- Passwords are hashed with bcrypt
- CORS is configured in `app/main.py`

### AI Integration
- AI model runs locally via llama.cpp
- MinerU requires valid API token for document processing
- Knowledge base must be populated for accurate diagnosis
- AI responses are parsed with regex patterns

### File Uploads
- Max file size: 200MB (configurable)
- Files stored in `/app/uploads/` in container
- Supported: PDF, images, documents
- MinerU extracts text content automatically

### Data Persistence
- PostgreSQL data in Docker volume `postgres_data`
- Redis data in Docker volume `redis_data`
- Uploads in Docker volume `uploads_data`

## Troubleshooting

**Port Already in Use**:
```bash
# Check what's using port 80/8000
sudo lsof -i :80
sudo lsof -i :8000
# Kill or change ports in docker-compose.yml
```

**Database Connection Failed**:
- Check postgres container is running: `docker-compose ps`
- Verify DATABASE_URL in environment
- Check logs: `docker-compose logs postgres`

**AI Diagnosis Not Working**:
- Verify AI_API_URL is accessible
- Check AI_API_KEY is correct
- Test AI endpoint directly with curl
- Check backend logs for error details

**Frontend Not Loading**:
- Check nginx is running: `docker-compose ps`
- Verify nginx.conf syntax
- Check nginx logs: `docker-compose logs nginx`

## Code Style Guidelines

### Python (Backend)
- Use type hints
- Async/await for all DB operations
- Follow FastAPI patterns
- Docstrings in Google style

### JavaScript (Frontend)
- Use async/await for API calls
- Proper error handling with try/catch
- Consistent indentation (2 spaces)

### SQL
- Use migrations for schema changes
- Index foreign keys
- Use appropriate data types

## Testing Checklist

Before submitting changes:
- [ ] Code follows style guidelines
- [ ] No hardcoded secrets
- [ ] Database migrations work (if applicable)
- [ ] API endpoints tested
- [ ] Frontend integration tested
- [ ] No console errors
- [ ] Docker build succeeds

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Docker Docs**: https://docs.docker.com/
- **Project README**: `/README.md`
- **Deployment Guide**: `/docs/DEPLOYMENT.md`
