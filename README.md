# QuizBattle 🎯

A comprehensive full-stack quiz platform built with Flask, React, PostgreSQL, and MongoDB. Features competitive challenges, real-time leaderboards, AI-powered question extraction, and secure admin management.

## 🏗️ Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for PostgreSQL
- **Flask-Migrate** - Database migrations
- **JWT** - Authentication
- **PostgreSQL** - Main database
- **MongoDB** - Logs and admin data
- **PyMongo** - MongoDB integration

### Frontend
- **React 18** - Frontend framework
- **React Router** - Client-side routing
- **Context API** - State management
- **Axios** - HTTP client
- **React Hot Toast** - Notifications
- **React Circular Progressbar** - Progress visualization

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Gunicorn** - WSGI server

## 📂 Project Structure

```
quizbattle/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utilities
│   ├── migrations/          # Database migrations
│   ├── tests/              # Unit tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Page components
│   │   ├── contexts/      # React contexts
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quizbattle
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - PostgreSQL: localhost:5432
   - MongoDB: localhost:27017

### Default Credentials
- **Admin Login**: username: `admin`, password: `admin123`

## 🔐 Authentication & Security

### User Authentication
- JWT-based authentication
- Secure password hashing with Werkzeug
- Role-based access control (user/admin)

### Admin Panel
- Separate admin authentication
- Session-based admin login
- Protected admin routes

## 📑 Features

### Core Features

#### User Features
- **Registration/Login** - Secure user authentication
- **Challenge Creation** - Create custom quiz challenges
- **Challenge Joining** - Join challenges via code or link
- **Quiz Playing** - Interactive quiz interface with timer
- **Results & Scoring** - Detailed results with scoring system
- **Leaderboard** - Monthly competitive rankings
- **Profile Management** - Update personal information

#### Admin Features
- **User Management** - View and manage users
- **Question Management** - CRUD operations for questions
- **PDF Upload** - AI-powered question extraction from PDFs
- **Challenge Management** - Monitor and control challenges
- **System Logs** - View MongoDB logs and activity
- **Dashboard Analytics** - System statistics and metrics

### Advanced Features

#### PDF Question Extraction
- **AI Classification** - Automatic difficulty assessment
- **Exam Type Detection** - CBSE, JEE Main/Advanced support
- **Hint Generation** - AI-generated hints for tough questions
- **Metadata Support** - Exam type and difficulty tagging

#### Challenge System
- **Custom Challenges** - Name, exam type, difficulty, question count, time limit
- **Mixed Difficulty** - 60% Easy + 40% Tough questions
- **Unique Codes** - 6-character challenge codes
- **Real-time Timer** - Countdown timer for challenges
- **One-time Submission** - Prevent multiple attempts

#### Scoring System
- **+4 points** for correct answers
- **-1 point** for wrong answers
- **Minimum score: 0** (no negative scores)
- **Monthly leaderboard** with automatic reset

## 🗄️ Database Design

### PostgreSQL (Main Data)
- **users** - User accounts and profiles
- **quiz_questions** - Question bank with metadata
- **challenges** - Challenge configurations
- **quiz_results** - User challenge results
- **leaderboard** - Monthly score tracking
- **admins** - Admin user accounts

### MongoDB (Logs & Analytics)
- **logs** - System activity and error logs
- **pdf_uploads** - PDF processing metadata
- **admin_actions** - Admin activity tracking

## 🐳 Docker Setup

### Services
- **postgres** - PostgreSQL database
- **mongodb** - MongoDB database
- **backend** - Flask API server
- **frontend** - React application

### Environment Variables
```bash
# Backend
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
DATABASE_URL=postgresql://quizbattle:password@postgres:5432/quizbattle
MONGODB_URL=mongodb://admin:password@mongodb:27017/
MONGODB_DB=quizbattle_logs

# Frontend
REACT_APP_API_URL=http://localhost:5000/api
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest
```

### Frontend Tests
```bash
cd frontend
npm install
npm test
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/admin/login` - Admin login
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/logout` - User logout

### Challenges
- `POST /api/challenges/create` - Create challenge
- `POST /api/challenges/join/{code}` - Join challenge
- `GET /api/challenges/{id}/play` - Get challenge questions
- `POST /api/challenges/{id}/submit` - Submit answers
- `GET /api/challenges/{id}/results` - Get challenge results
- `GET /api/challenges/active` - Get active challenges

### Admin
- `GET /api/admin/dashboard` - Admin dashboard
- `GET /api/admin/users` - Manage users
- `GET /api/admin/questions` - Manage questions
- `POST /api/admin/upload-pdf` - Upload PDF
- `GET /api/admin/logs` - View system logs

## 🔧 Development

### Local Development Setup

1. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   python run.py
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

3. **Database Setup**
   ```bash
   # Start PostgreSQL and MongoDB
   docker-compose up postgres mongodb -d
   
   # Initialize database
   flask db upgrade
   flask init-db
   ```

### Environment Configuration
Copy `backend/env.example` to `backend/.env` and configure:
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://quizbattle:password@localhost:5432/quizbattle
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB=quizbattle_logs
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

## 🚀 Deployment

### Production Deployment
1. Update environment variables for production
2. Use production-grade secrets
3. Configure reverse proxy (nginx)
4. Set up SSL certificates
5. Use production database instances

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API endpoints

## 🔮 Future Enhancements

- [ ] Real-time multiplayer challenges
- [ ] Advanced AI question generation
- [ ] Mobile app development
- [ ] Social features and friend challenges
- [ ] Advanced analytics and reporting
- [ ] Integration with external quiz APIs
- [ ] Gamification elements (badges, achievements)
- [ ] Video question support
- [ ] Offline mode support

---

**QuizBattle** - Where knowledge meets competition! 🏆
