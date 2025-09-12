# Создаем Backend файлы

# Backend requirements.txt
requirements = """# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9

# Redis
redis==5.0.1
hiredis==2.2.3

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Email
fastapi-mail==1.4.1

# HTTP client
httpx==0.25.2
aiofiles==23.2.1

# Utilities
python-dateutil==2.8.2
email-validator==2.1.0

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Monitoring
prometheus-client==0.19.0
"""

# Backend Dockerfile
backend_dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
        curl \\
        libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# Core config.py
config_py = """from functools import lru_cache
from typing import Optional, List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PairLingua API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Email (optional)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
"""

# Core database.py
database_py = """from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create engine
if settings.ENVIRONMENT == "testing":
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=settings.DEBUG
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=settings.DEBUG
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""

# Core redis.py
redis_py = """import redis.asyncio as redis
from app.core.config import settings

# Redis connection
redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
    retry_on_timeout=True,
    socket_keepalive=True,
    socket_keepalive_options={}
)


async def get_redis():
    return redis_client


class RedisService:
    def __init__(self):
        self.redis = redis_client
    
    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None) -> bool:
        return await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        return await self.redis.delete(key)
    
    async def exists(self, key: str) -> int:
        return await self.redis.exists(key)
    
    async def expire(self, key: str, time: int) -> bool:
        return await self.redis.expire(key, time)
    
    async def sadd(self, key: str, *values) -> int:
        return await self.redis.sadd(key, *values)
    
    async def sismember(self, key: str, value: str) -> bool:
        return await self.redis.sismember(key, value)


redis_service = RedisService()
"""

# Core security.py
security_py = """from datetime import datetime, timedelta
from typing import Optional, Union, Any
import uuid
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token types
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def create_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = func.now() + expires_delta
    else:
        expire = func.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    jti = str(uuid.uuid4())
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": TOKEN_TYPE_ACCESS,
        "jti": jti
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = func.now() + expires_delta
    else:
        expire = func.now() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    
    jti = str(uuid.uuid4())
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": TOKEN_TYPE_REFRESH,
        "jti": jti
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_REFRESH_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> dict:
    try:
        secret_key = (
            settings.JWT_SECRET_KEY if token_type == TOKEN_TYPE_ACCESS 
            else settings.JWT_REFRESH_SECRET_KEY
        )
        payload = jwt.decode(
            token, secret_key, algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
"""

# Core exceptions.py
exceptions_py = """from fastapi import HTTPException, status


class PairLinguaException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationException(PairLinguaException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(PairLinguaException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationException(PairLinguaException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class NotFoundException(PairLinguaException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ConflictException(PairLinguaException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status.HTTP_409_CONFLICT)


class RateLimitException(PairLinguaException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)
"""

# Записываем файлы backend
with open("pairlingua/backend/requirements.txt", "w") as f:
    f.write(requirements)

with open("pairlingua/backend/Dockerfile", "w") as f:
    f.write(backend_dockerfile)

with open("pairlingua/backend/app/core/config.py", "w") as f:
    f.write(config_py)

with open("pairlingua/backend/app/core/database.py", "w") as f:
    f.write(database_py)

with open("pairlingua/backend/app/core/redis.py", "w") as f:
    f.write(redis_py)

with open("pairlingua/backend/app/core/security.py", "w") as f:
    f.write(security_py)

with open("pairlingua/backend/app/core/exceptions.py", "w") as f:
    f.write(exceptions_py)

print("✅ Backend Core модули созданы")
print("📦 Requirements.txt с зависимостями")
print("🐳 Dockerfile для backend")
print("⚙️ Конфигурация, БД, Redis, Security")