from datetime import datetime, timedelta
from typing import Optional, Union, Any
import uuid
import bcrypt
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def create_password_hash(password: str) -> str:
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed.decode()
    raise ValueError('password is not a string')



def verify_password(plain_password: str, hashed_password: str) -> bool:
    assert isinstance(plain_password, str), f'plain_password not str, got {type(plain_password)}'
    assert isinstance(hashed_password, str), f'hashed_password not str, got {type(hashed_password)}'
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    expire_time = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    jti = str(uuid.uuid4())
    to_encode = {
        "exp": expire_time,
        "sub": str(subject),
        "type": TOKEN_TYPE_ACCESS,
        "jti": jti,
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    jti = str(uuid.uuid4())
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "type": TOKEN_TYPE_REFRESH,
        "jti": jti,
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str, token_type: str = TOKEN_TYPE_ACCESS) -> dict:
    try:
        secret_key = settings.JWT_SECRET_KEY if token_type == TOKEN_TYPE_ACCESS else settings.JWT_REFRESH_SECRET_KEY
        payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
