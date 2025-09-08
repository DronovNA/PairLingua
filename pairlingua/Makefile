# PairLingua Makefile

.PHONY: help build up down logs clean test lint format

# Default target
help:
	@echo "PairLingua Development Commands"
	@echo "==============================="
	@echo "build      - Build Docker images"
	@echo "up         - Start all services"
	@echo "down       - Stop all services"
	@echo "logs       - Show service logs"
	@echo "clean      - Clean up containers and volumes"
	@echo "test       - Run tests"
	@echo "lint       - Run linters"
	@echo "format     - Format code"
	@echo "migrate    - Run database migrations"
	@echo "seed       - Seed database with sample data"
	@echo "shell-be   - Backend shell"
	@echo "shell-fe   - Frontend shell"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 10
	@echo "Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --rmi all --remove-orphans
	docker system prune -f

# Development commands
test:
	@echo "Running backend tests..."
	cd backend && python -m pytest --cov=app tests/
	@echo "Running frontend tests..."
	cd frontend && npm test -- --coverage --watchAll=false

lint:
	@echo "Linting backend..."
	cd backend && python -m flake8 app/
	cd backend && python -m black --check app/
	cd backend && python -m isort --check-only app/
	@echo "Linting frontend..."
	cd frontend && npm run lint

format:
	@echo "Formatting backend code..."
	cd backend && python -m black app/
	cd backend && python -m isort app/
	@echo "Formatting frontend code..."
	cd frontend && npm run lint:fix

# Database commands
migrate:
	docker-compose exec backend alembic upgrade head

seed:
	docker-compose exec postgres psql -U postgres -d pairlingua -f /docker-entrypoint-initdb.d/02-seed.sql

# Shell access
shell-be:
	docker-compose exec backend /bin/bash

shell-fe:
	docker-compose exec frontend /bin/sh

# Quick setup for new developers
setup: build up migrate
	@echo "Setup complete! Application is ready."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000/docs"

# Production build
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Health check
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/api/v1/health || echo "Backend not responding"
	@curl -f http://localhost:3000 || echo "Frontend not responding"
