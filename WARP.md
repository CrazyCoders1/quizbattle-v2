# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

QuizBattle is a full-stack quiz platform built specifically for JEE (Joint Entrance Examination) students and educators. The system features AI-powered PDF question extraction, real-time competitive challenges, and comprehensive admin management tools.

**Tech Stack:**
- **Backend:** Flask, PostgreSQL (Neon), MongoDB (Atlas), Redis
- **Frontend:** React 18, Tailwind CSS, Axios
- **AI Integration:** OpenRouter API with DeepSeek models
- **Deployment:** Render (backend) + Netlify (frontend), Docker for local development

## Essential Commands

### Development Commands

**Backend Development:**
```bash
# Setup and run backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python run.py

# Database operations
flask db init
flask db migrate -m "Migration message"
flask db upgrade
flask init-db  # Create sample data
```

**Frontend Development:**
```bash
# Setup and run frontend
cd frontend
npm install
npm start

# Build for production
npm run build
```

**Testing Commands:**
```bash
# Backend API testing
cd backend
python simple_api_test.py
python test_api_endpoints.py

# Comprehensive E2E testing
python comprehensive_e2e_test.py

# PDF extraction testing
python test_pdf_extraction.py
```

### Docker Development

**Local development with Docker:**
```bash
# Start all services
docker-compose up --build

# Start specific services
docker-compose up postgres mongodb -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Deployment Commands

**Production deployment (Render + Netlify):**
```bash
# Manual deployment verification
cd backend
python check_deployment.py
python validate_production_api.py

# Database seeding for production
python production_db_seed.py
```

## Architecture Overview

### Backend Architecture (Flask)

The backend follows a modular Flask blueprint pattern:

**Core Structure:**
- `app/__init__.py` - Application factory with SQLAlchemy, JWT, MongoDB setup
- `app/models/` - Database models (User, Challenge, QuizQuestion, QuizResult, Leaderboard, Admin)
- `app/routes/` - API blueprints organized by functionality
- `app/services/` - Business logic services (implied from usage patterns)

**Key Blueprints:**
- `auth_bp` (`/api/auth`) - User/admin authentication
- `challenges_bp` (`/api/challenges`) - Challenge CRUD and participation
- `admin_bp` (`/api/admin`) - Admin panel operations, PDF uploads
- `leaderboard_bp` (`/api/leaderboard`) - Scoring and rankings
- `debug_bp` (`/api/debug`) - Development debugging tools

**Database Design:**
- **PostgreSQL** - Primary data (users, questions, challenges, results)
- **MongoDB** - Logging, analytics, PDF processing metadata
- **Redis** - Caching, rate limiting, session management

### Frontend Architecture (React)

**Component Structure:**
- `src/components/` - Reusable UI components
- `src/pages/` - Page-level components (Home, Admin, Challenges, etc.)
- `src/contexts/AuthContext.js` - Global authentication state
- `src/services/apiService.js` - Centralized API client with Axios

**Key Features:**
- JWT-based authentication with automatic token refresh
- Role-based routing (user vs admin access)
- Real-time quiz timer and progress tracking
- Responsive design with Tailwind CSS

### AI Integration Architecture

**PDF Question Extraction Pipeline:**
1. **Upload Processing** - PDF parsing with PyPDF2/pdfplumber
2. **AI Analysis** - OpenRouter API with DeepSeek models for content extraction
3. **Content Cleaning** - Remove ads, format questions, validate answers
4. **Difficulty Classification** - Automatic categorization (easy/tough/mixed)
5. **Database Storage** - Structured question storage with metadata

**Fallback Strategy:**
- Primary: OpenRouter + DeepSeek
- Secondary: Multiple AI providers (OpenAI, Gemini, Claude)
- Tertiary: Regex-based extraction for reliability

## Database Management

### PostgreSQL Operations

**Connection handling:**
- Uses psycopg2-binary for compatibility
- Connection pooling configured in `app/__init__.py`
- URL conversion: `postgres://` → `postgresql://` for psycopg2

**Migration workflow:**
```bash
flask db init      # Initialize migrations (first time)
flask db migrate   # Generate migration
flask db upgrade   # Apply migrations
flask init-db      # Seed with sample data
```

**Key Models:**
- `User` - Student/user accounts with JWT auth
- `Admin` - Separate admin authentication system
- `QuizQuestion` - Questions with difficulty, exam_type, options
- `Challenge` - Quiz instances with codes, time limits
- `QuizResult` - User challenge submissions and scores
- `Leaderboard` - Monthly competitive rankings

### MongoDB Operations

**Usage patterns:**
- System logging and error tracking
- PDF processing metadata and history
- Admin activity monitoring

**Connection:**
- Configured via `MONGO_URI` environment variable
- Graceful degradation if MongoDB unavailable

## Testing Strategy

### Test Organization

**Unit Tests:**
- `simple_api_test.py` - Basic API functionality verification
- `test_api_endpoints.py` - Comprehensive endpoint testing
- `test_pdf_extraction.py` - PDF processing validation

**Integration Tests:**
- `comprehensive_e2e_test.py` - Full workflow testing with concurrent users
- `test_complete_workflow.py` - End-to-end feature testing

**Production Testing:**
- `validate_production_api.py` - Live environment verification
- `test_production_db.py` - Database connectivity and performance

### Critical Testing Areas

1. **PDF Extraction Pipeline** - AI processing, content cleaning, answer mapping
2. **Authentication Flow** - JWT handling, role-based access
3. **Challenge System** - Code generation, question selection, scoring
4. **Admin Operations** - Bulk delete, user management, question filtering
5. **Database Integrity** - Migration safety, data consistency

## Deployment Architecture

### Production Stack

**Render (Backend):**
- Flask app with Gunicorn WSGI server
- Auto-scaling with connection pooling
- Environment variables for configuration
- Health checks at `/health`

**Netlify (Frontend):**
- React SPA with CDN distribution  
- Automatic builds from Git
- Environment variable management
- SPA routing with redirects

**External Services:**
- **Neon** - Serverless PostgreSQL database
- **MongoDB Atlas** - Cloud MongoDB for logging
- **OpenRouter** - AI API for PDF extraction

### Environment Configuration

**Critical Environment Variables:**
```bash
# Backend (.env or Render dashboard)
JWT_SECRET=your-secret-key
DATABASE_URL=postgresql://...  # Neon PostgreSQL
MONGO_URI=mongodb+srv://...    # MongoDB Atlas
OPENROUTER_API_KEY=sk-or-...   # AI processing
FLASK_ENV=production
PORT=10000

# Frontend (Netlify dashboard)  
REACT_APP_API_URL=https://your-backend.onrender.com/api
```

## Development Practices

### Code Patterns

**Backend Patterns:**
- Blueprint-based route organization
- JWT authentication decorators (`@jwt_required()`)
- Database session management with rollback error handling
- Logging with structured format using `current_app.logger`

**Frontend Patterns:**
- Context API for global state (authentication)
- Protected routes with role checking
- Axios interceptors for token management
- Toast notifications for user feedback

### Error Handling

**Backend Error Strategy:**
- Try-catch blocks with database rollbacks
- Structured error responses with HTTP status codes
- Comprehensive logging for debugging
- Graceful degradation for external services

**Frontend Error Strategy:**
- Global error boundaries for React components
- API error handling with user-friendly messages
- Loading states and progress indicators
- Offline handling considerations

## AI Integration Guidelines

### PDF Processing Workflow

**Input Requirements:**
- JEE Main/Advanced physics question papers
- PDF format with selectable text
- Standard question-option-answer structure

**Processing Steps:**
1. Text extraction with content cleaning
2. AI analysis for question identification
3. Answer validation and option mapping
4. Difficulty classification
5. Database insertion with metadata

**Quality Assurance:**
- Answer accuracy validation (100% target)
- Option format standardization
- Content deduplication
- Difficulty consistency checks

### AI API Management

**Rate Limiting:**
- Respect OpenRouter API limits
- Implement retry logic with exponential backoff
- Queue processing for bulk operations
- Cost monitoring for API usage

**Error Recovery:**
- Multiple AI provider fallbacks
- Regex-based extraction as last resort
- Partial processing continuation
- Manual review flagging for problematic content

## Security Considerations

### Authentication Security

**JWT Implementation:**
- Short-lived access tokens (1 hour)
- Secure secret key management
- Token blacklisting on logout
- Role-based access control

**Password Security:**
- PBKDF2-SHA256 hashing
- Minimum complexity requirements
- Secure admin credential management
- Password reset functionality

### API Security

**Protection Measures:**
- CORS configuration for allowed origins
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy ORM

### Production Security

**Infrastructure Security:**
- HTTPS enforcement
- Environment variable management
- Database connection encryption
- Secure headers implementation

This architecture supports rapid development while maintaining production-grade security and scalability. The modular design allows for independent scaling of components and easy feature additions.