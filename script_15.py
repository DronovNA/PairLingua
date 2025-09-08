# Создаем Docker Compose и остальные конфигурационные файлы

# Docker Compose файл
docker_compose = """version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: pairlingua-postgres
    environment:
      POSTGRES_DB: ${DB_NAME:-pairlingua}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./scripts/seed-data.sql:/docker-entrypoint-initdb.d/02-seed.sql
    ports:
      - "${DB_PORT:-5432}:5432"
    networks:
      - pairlingua-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: pairlingua-redis
    command: redis-server --requirepass ${REDIS_PASSWORD:-redis123} --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    networks:
      - pairlingua-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-redis123}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: pairlingua-backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-postgres}@postgres:5432/${DB_NAME:-pairlingua}
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis123}@redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-super-secret-jwt-key-change-this-in-production}
      - JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY:-your-super-secret-refresh-key-change-this-too}
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000,http://localhost}
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - DEBUG=${DEBUG:-true}
    volumes:
      - ./backend/app:/app/app
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - pairlingua-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pairlingua-frontend
    environment:
      - REACT_APP_API_BASE_URL=${REACT_APP_API_BASE_URL:-http://localhost:8000/api/v1}
      - REACT_APP_ENVIRONMENT=${ENVIRONMENT:-development}
    ports:
      - "${FRONTEND_PORT:-3000}:80"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - pairlingua-network
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: pairlingua-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    ports:
      - "${NGINX_PORT:-80}:80"
      - "${NGINX_SSL_PORT:-443}:443"
    depends_on:
      - frontend
      - backend
    networks:
      - pairlingua-network
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  pairlingua-network:
    driver: bridge
"""

# Environment файл
env_example = """# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pairlingua
DB_USER=postgres
DB_PASSWORD=postgres

# Redis Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis123

# JWT Configuration (CHANGE IN PRODUCTION!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production-make-it-at-least-32-characters-long
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-change-this-too-make-it-different-from-access-key

# Application Configuration
ENVIRONMENT=development
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost

# API Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
NGINX_SSL_PORT=443

# Frontend Configuration
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development

# Email Configuration (Optional)
SMTP_SERVER=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=

# Production Settings (Set in production)
# POSTGRES_HOST=your-production-db-host
# REDIS_HOST=your-production-redis-host
# DOMAIN=yourdomain.com
"""

# Nginx конфигурация
nginx_conf = """events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:80;
    }

    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout  65;
    types_hash_max_size 2048;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
"""

nginx_default_conf = """server {
    listen 80;
    server_name localhost;

    client_max_body_size 100M;

    # Frontend (React)
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Handle WebSocket connections
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '$http_origin' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, PATCH, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
}
"""

# README файл
readme_md = """# PairLingua - Interactive Spanish-Russian Language Learning App

PairLingua is a modern, interactive web application for learning Spanish through Russian translations using spaced repetition algorithms and gamification.

## 🎯 Features

- **Spaced Repetition Learning**: Uses SM-2 algorithm for optimal retention
- **Interactive Exercises**: Matching, multiple choice, and typing exercises
- **Gamification**: Points, streaks, achievements, and leaderboards
- **Progress Tracking**: Detailed statistics and learning analytics
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile
- **Real-time Updates**: Instant feedback and progress updates

## 🏗️ Architecture

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python 3.11
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Reverse Proxy**: Nginx
- **Containerization**: Docker + Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pairlingua.git
   cd pairlingua
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Wait for services to be ready** (about 30-60 seconds)

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Demo Account

- Email: `demo@pairlingua.com`
- Password: `demo123`

## 📁 Project Structure

```
pairlingua/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom hooks
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # Redux store
│   │   └── types/          # TypeScript types
│   ├── Dockerfile
│   └── package.json
├── nginx/                   # Nginx configuration
├── scripts/                 # Database scripts
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔧 Development

### Backend Development

1. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

2. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

3. **Start development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

### Database Management

- **Create migration**: `alembic revision --autogenerate -m "Description"`
- **Apply migrations**: `alembic upgrade head`
- **Rollback migration**: `alembic downgrade -1`

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests
```bash
npm run test:e2e
```

## 📊 API Documentation

The API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- **Authentication**
  - `POST /api/v1/auth/register` - Register new user
  - `POST /api/v1/auth/login` - Login user
  - `POST /api/v1/auth/refresh` - Refresh tokens

- **Study**
  - `GET /api/v1/study/cards/due` - Get cards due for review
  - `POST /api/v1/study/cards/review` - Submit review results

- **User**
  - `GET /api/v1/users/me` - Get current user profile
  - `GET /api/v1/users/me/stats` - Get user statistics

## 🏆 Learning Algorithm

PairLingua uses the **SM-2 (SuperMemo 2)** spaced repetition algorithm:

1. **Quality Scale (0-5)**:
   - 0: Complete blackout
   - 1: Incorrect response; correct one remembered
   - 2: Incorrect response; correct one seemed easy
   - 3: Correct response recalled with serious difficulty
   - 4: Correct response after hesitation
   - 5: Perfect response

2. **Adaptive Intervals**: Cards are scheduled for review at increasing intervals based on performance

3. **Ease Factor**: Each card has a difficulty factor that adjusts based on response quality

## 🎮 Game Elements

- **Points System**: Earn points for correct answers
- **Streak Tracking**: Maintain daily study streaks
- **Achievements**: Unlock badges for milestones
- **Leaderboards**: Compete with other learners
- **Progress Visualization**: Charts and statistics

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt with salt
- **CORS Protection**: Configurable origins
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Server-side data validation

## 📱 Mobile Support

- Responsive design for all screen sizes
- Touch-friendly interface
- PWA (Progressive Web App) support
- Offline functionality (coming soon)

## 🌍 Internationalization

- Multi-language interface (Russian, Spanish, English)
- RTL language support
- Locale-specific formatting

## 📈 Monitoring & Analytics

- Health check endpoints
- Performance metrics
- Error tracking
- User analytics

## 🚀 Deployment

### Production Deployment

1. **Set production environment variables**
2. **Build Docker images**
3. **Deploy with Docker Compose or Kubernetes**
4. **Set up SSL certificates**
5. **Configure domain and DNS**

### Environment Variables

See `.env.example` for all available configuration options.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [Wiki](https://github.com/yourusername/pairlingua/wiki)
- Issues: [GitHub Issues](https://github.com/yourusername/pairlingua/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/pairlingua/discussions)

## 🙏 Acknowledgments

- SuperMemo for the SM-2 algorithm
- OpenAI for language processing inspiration
- The open-source community for amazing tools and libraries

---

**PairLingua** - Making language learning interactive, effective, and fun! 🎉
"""

# Makefile для удобства разработки
makefile = """# PairLingua Makefile

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
"""

# Frontend nginx конфигурация
frontend_nginx_conf = """server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/javascript
        application/javascript
        application/json
        application/xml
        application/rss+xml
        application/atom+xml
        image/svg+xml;

    # Handle React Router
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \\.(?:ico|css|js|gif|jpe?g|png|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }

    # Security
    location ~ /\\. {
        deny all;
    }
}
"""

# VSCode настройки
vscode_settings = """{
  "editor.tabSize": 2,
  "editor.insertSpaces": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.blackEnabled": true,
  "python.formatting.provider": "black",
  "[python]": {
    "editor.tabSize": 4,
    "editor.rulers": [88]
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/node_modules": true,
    "**/build": true,
    "**/dist": true
  }
}
"""

# Записываем все файлы
with open("pairlingua/docker-compose.yml", "w") as f:
    f.write(docker_compose)

with open("pairlingua/.env.example", "w") as f:
    f.write(env_example)

with open("pairlingua/nginx/nginx.conf", "w") as f:
    f.write(nginx_conf)

with open("pairlingua/nginx/default.conf", "w") as f:
    f.write(nginx_default_conf)

with open("pairlingua/README.md", "w", encoding="utf-8") as f:
    f.write(readme_md)

with open("pairlingua/Makefile", "w") as f:
    f.write(makefile)

with open("pairlingua/frontend/nginx.conf", "w") as f:
    f.write(frontend_nginx_conf)

with open("pairlingua/.vscode/settings.json", "w", encoding="utf-8") as f:
    f.write(vscode_settings)

print("✅ Docker Compose и конфигурация созданы")
print("🐳 Docker Compose с PostgreSQL, Redis, Nginx")
print("📝 README с подробной документацией")
print("⚙️ Environment файлы и настройки")
print("🔧 Makefile для удобства разработки")
print("📁 VSCode настройки для проекта")