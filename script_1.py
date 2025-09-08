# Создаем основные конфигурационные файлы

# Docker Compose
docker_compose = """version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: pairlingua_postgres
    environment:
      POSTGRES_DB: ${DB_NAME:-pairlingua}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
      - ./scripts/seed-data.sql:/docker-entrypoint-initdb.d/seed-data.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: pairlingua_redis
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-redis_pass}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: pairlingua_backend
    environment:
      - DATABASE_URL=postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-postgres}@postgres:5432/${DB_NAME:-pairlingua}
      - REDIS_URL=redis://default:${REDIS_PASSWORD:-redis_pass}@redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-your-secret-key-change-in-production}
      - JWT_REFRESH_SECRET_KEY=${JWT_REFRESH_SECRET_KEY:-your-refresh-secret-key-change-in-production}
      - ENVIRONMENT=${ENVIRONMENT:-development}
      - CORS_ORIGINS=${CORS_ORIGINS:-http://localhost:3000}
    volumes:
      - ./backend/app:/app/app
      - ./backend/alembic:/app/alembic
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
      "

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: pairlingua_frontend
    environment:
      - REACT_APP_API_BASE_URL=${API_BASE_URL:-http://localhost:8000}
      - NODE_ENV=${NODE_ENV:-development}
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    ports:
      - "3000:3000"
    depends_on:
      - backend
    stdin_open: true
    tty: true

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    container_name: pairlingua_nginx
    ports:
      - "80:80"
    depends_on:
      - backend
      - frontend
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    driver: bridge
"""

# .env.example
env_example = """# Database
DB_NAME=pairlingua
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_PASSWORD=redis_pass
REDIS_HOST=localhost
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_REFRESH_SECRET_KEY=your-super-secret-refresh-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API
API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
DEBUG=true

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend
NODE_ENV=development
REACT_APP_API_BASE_URL=http://localhost:8000
"""

# .gitignore
gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# React
/build
.env.local
.env.development.local
.env.test.local
.env.production.local

# Database
*.db
*.sqlite

# Docker
.dockerignore

# Logs
logs/
*.log

# Testing
coverage/
.nyc_output/
.coverage

# Alembic
alembic.ini.bak
"""

# README.md
readme = """# PairLingua - Изучение испанского языка

Интерактивное веб-приложение для изучения испанского языка через составление пар слов с использованием алгоритма spaced repetition.

## Технологии

- **Backend**: FastAPI, PostgreSQL, Redis, JWT
- **Frontend**: React 18, TypeScript, TailwindCSS, Redux Toolkit
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Algorithms**: SM-2 spaced repetition
- **Architecture**: Modular monolith ready for microservices

## Функциональность

- 🔐 Регистрация и авторизация пользователей
- 🎮 Интерактивные игровые упражнения (matching, multiple choice, typing)
- 🧠 Алгоритм интервальных повторений SM-2
- 📊 Детальная статистика и прогресс
- 🏆 Система достижений и геймификация
- 📱 Адаптивный дизайн для всех устройств
- 🌐 Мультиязычность (русский/испанский)

## Быстрый старт

### Требования

- Docker и Docker Compose
- Git

### Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd pairlingua
```

2. Скопируйте файл окружения:
```bash
cp .env.example .env
```

3. Запустите приложение:
```bash
docker-compose up --build
```

### Доступ к приложению

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Nginx Proxy: http://localhost:80

## Разработка

### Структура проекта

```
pairlingua/
├── backend/           # FastAPI приложение
│   ├── app/
│   │   ├── api/       # REST API endpoints
│   │   ├── core/      # Конфигурация, БД, безопасность
│   │   ├── models/    # SQLAlchemy модели
│   │   ├── schemas/   # Pydantic схемы
│   │   ├── services/  # Бизнес-логика
│   │   └── utils/     # Утилиты
│   └── tests/         # Тесты
├── frontend/          # React приложение
│   └── src/
│       ├── components/ # React компоненты
│       ├── hooks/     # Кастомные хуки
│       ├── services/  # API клиенты
│       ├── store/     # Redux store
│       └── types/     # TypeScript типы
├── nginx/             # Reverse proxy конфигурация
└── scripts/           # SQL скрипты и утилиты
```

### API Endpoints

#### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена
- `POST /api/v1/auth/logout` - Выход

#### Изучение
- `GET /api/v1/study/cards/due` - Получить карточки для изучения
- `POST /api/v1/study/cards/review` - Отправить результаты изучения
- `POST /api/v1/study/session/replace` - Заменить изученную карточку

#### Профиль и статистика
- `GET /api/v1/users/me` - Профиль пользователя
- `GET /api/v1/users/me/stats` - Статистика пользователя
- `PATCH /api/v1/users/me` - Обновить профиль

### Тестирование

#### Backend тесты
```bash
cd backend
pytest tests/ -v --cov=app
```

#### Frontend тесты
```bash
cd frontend
npm test
```

### База данных

#### Миграции
```bash
# Создать миграцию
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Применить миграции
docker-compose exec backend alembic upgrade head

# Откат миграции
docker-compose exec backend alembic downgrade -1
```

### Производительность

- Медианная латентность API < 150ms
- P95 latency < 300ms
- Поддержка 500 RPS на 2 vCPU/4GB RAM
- Redis кэширование для due-подборок
- Оптимизированные SQL запросы с индексами

### Безопасность

- JWT токены с коротким временем жизни (15 мин access, 7 дней refresh)
- Bcrypt хэширование паролей
- Rate limiting для защиты от brute force
- CORS и CSRF защита
- Валидация всех входных данных

## Алгоритм обучения

Приложение использует алгоритм SM-2 для оптимального интервального повторения:

- **Quality** (0-5): оценка качества ответа пользователя
- **Ease Factor**: начальное значение 2.5, корректируется по качеству ответов  
- **Interval**: интервал до следующего показа карточки
- **Repetition Count**: количество успешных повторений

### Типы упражнений

1. **Matching** - сопоставление слов
2. **Multiple Choice** - выбор из 4 вариантов
3. **Typing** - ввод перевода с проверкой
4. **Audio** - прослушивание и выбор (планируется)

## Развертывание в продакшене

### Переменные окружения
Обязательно измените в `.env`:
- `JWT_SECRET_KEY` и `JWT_REFRESH_SECRET_KEY`
- Пароли для БД и Redis
- CORS_ORIGINS на ваш домен

### SSL/TLS
Для продакшена настройте HTTPS в nginx конфигурации.

### Мониторинг
- Health checks на `/api/v1/health`
- Prometheus метрики на `/api/v1/metrics`
- Логирование в stdout для Docker

## Вклад в проект

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Лицензия

MIT License - подробности в файле LICENSE.

## Поддержка

- 📧 Email: support@pairlingua.com
- 💬 Issues: GitHub Issues
- 📚 Docs: /docs в API
"""

# Записываем файлы
with open("pairlingua/docker-compose.yml", "w", encoding="utf-8") as f:
    f.write(docker_compose)

with open("pairlingua/.env.example", "w", encoding="utf-8") as f:
    f.write(env_example)

with open("pairlingua/.gitignore", "w", encoding="utf-8") as f:
    f.write(gitignore)

with open("pairlingua/README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("✅ Основные конфигурационные файлы созданы")
print("📝 Создан README с подробной документацией")
print("🐳 Docker Compose конфигурация готова")