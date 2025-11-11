#!/bin/bash

# PairLingua Application Start Script
set -e

echo "🚀 Starting PairLingua Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

echo "🔧 Environment: $ENVIRONMENT"

# Wait for services to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "localhost" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
    >&2 echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "✅ PostgreSQL is ready!"

echo "⏳ Waiting for Redis to be ready..."
until redis-cli -h localhost -p 6379 -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; do
    >&2 echo "Redis is unavailable - sleeping"
    sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🗄️ Running database migrations..."
cd backend
alembic upgrade head
cd ..

echo "🎉 PairLingua is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "🛑 To stop all services: docker-compose down"
echo "📋 To view logs: docker-compose logs -f"
