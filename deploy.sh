#!/bin/bash

# QuizBattle Production Deployment Script
set -e

echo "🚀 Starting QuizBattle Production Deployment"
echo "=============================================="

# Check if .env files exist
if [ ! -f "backend/.env.production" ]; then
    echo "❌ Error: backend/.env.production not found"
    echo "Please create the production environment file with your configuration"
    exit 1
fi

if [ ! -f "frontend/.env.production" ]; then
    echo "❌ Error: frontend/.env.production not found"
    echo "Please create the frontend production environment file"
    exit 1
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    exit 1
fi

# Load production environment variables
source backend/.env.production

# Validate required environment variables
REQUIRED_VARS=("POSTGRES_PASSWORD" "MONGO_PASSWORD" "SECRET_KEY" "JWT_SECRET_KEY" "OPENROUTER_API_KEY")

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Create necessary directories
mkdir -p logs uploads nginx/ssl

echo "✅ Directories created"

# Generate SSL certificates (self-signed for testing)
if [ ! -f "nginx/ssl/cert.pem" ]; then
    echo "🔐 Generating self-signed SSL certificates (replace with real certificates in production)"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
    echo "✅ SSL certificates generated"
fi

# Build and start services
echo "🐳 Building and starting Docker containers..."

# Stop any existing containers
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Build and start services
docker-compose -f docker-compose.prod.yml up --build -d

echo "⏳ Waiting for services to be ready..."

# Wait for PostgreSQL
echo "📊 Waiting for PostgreSQL..."
until docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U quizbattle_user -d quizbattle_prod; do
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for MongoDB
echo "🍃 Waiting for MongoDB..."
sleep 10
echo "✅ MongoDB is ready"

# Wait for backend
echo "🐍 Waiting for backend..."
until curl -f http://localhost:5000/health &> /dev/null; do
    sleep 2
done
echo "✅ Backend is ready"

# Wait for frontend
echo "⚛️ Waiting for frontend..."
until curl -f http://localhost:3000/health &> /dev/null; do
    sleep 2
done
echo "✅ Frontend is ready"

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
echo "✅ Database migrations completed"

# Create default admin user
echo "👨‍💼 Creating default admin user..."
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app import create_app
from app.models import User
from app import db

app = create_app()
with app.app_context():
    admin = User.query.filter_by(username='$DEFAULT_ADMIN_USERNAME').first()
    if not admin:
        admin = User(
            username='$DEFAULT_ADMIN_USERNAME',
            email='$DEFAULT_ADMIN_EMAIL',
            is_admin=True
        )
        admin.set_password('$DEFAULT_ADMIN_PASSWORD')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created successfully')
    else:
        print('Admin user already exists')
"
echo "✅ Admin user setup completed"

# Display status
echo ""
echo "🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "===================================="
echo ""
echo "🌐 Services Status:"
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "🔗 Access URLs:"
echo "   Frontend: https://localhost (or your domain)"
echo "   Backend API: https://localhost/api"
echo "   Admin Panel: https://localhost/admin"
echo ""
echo "👨‍💼 Admin Credentials:"
echo "   Username: $DEFAULT_ADMIN_USERNAME"
echo "   Password: $DEFAULT_ADMIN_PASSWORD"
echo ""
echo "📊 Monitoring:"
echo "   Logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop: docker-compose -f docker-compose.prod.yml down"
echo ""
echo "⚠️  Important Notes:"
echo "   1. Replace self-signed SSL certificates with real ones"
echo "   2. Update domain names in nginx.conf"
echo "   3. Set up proper database backups"
echo "   4. Configure monitoring and alerting"
echo "   5. Set up log rotation"
echo ""
echo "✅ QuizBattle is now running in production mode!"