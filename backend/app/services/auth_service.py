from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.core.security import (
    verify_password, create_password_hash, 
    create_access_token, create_refresh_token, decode_token
)
from app.core.exceptions import AuthenticationException, ConflictException
from app.models.user import User, TokenBlacklist
from app.schemas.auth import UserRegister, UserLogin, Token
from app.core.redis import redis_service


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UserRegister) -> User:
        """Register a new user"""
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            User.email == user_data.email
        ).first()
        
        if existing_user:
            raise ConflictException("User with this email already exists")
        
        # Check nickname uniqueness
        if user_data.nickname:
            existing_nickname = self.db.query(User).filter(
                User.nickname == user_data.nickname
            ).first()
            if existing_nickname:
                raise ConflictException("Nickname already taken")
        
        # Create new user
        password = user_data.password[:72]
        user = User(
            email=user_data.email,
            password_hash=create_password_hash(password),
            nickname=user_data.nickname,
            locale=user_data.locale
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def authenticate_user(self, credentials: UserLogin) -> Token:
        """Authenticate user and return tokens"""
        
        user = self.db.query(User).filter(
            User.email == credentials.email,
            User.is_active == True,
            User.deleted_at.is_(None)
        ).first()
        
        if not user or not verify_password(credentials.password, user.password_hash):
            raise AuthenticationException("Invalid email or password")
        
        # Update last login
        user.last_login = func.now()
        self.db.commit()
        
        # Create tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60  # 15 minutes
        )
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        
        try:
            payload = decode_token(refresh_token, "refresh")
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            if not user_id or not jti:
                raise AuthenticationException("Invalid refresh token")
            
            # Check if token is blacklisted
            blacklisted = self.db.query(TokenBlacklist).filter(
                TokenBlacklist.jti == jti
            ).first()
            
            if blacklisted:
                raise AuthenticationException("Token has been revoked")
            
            # Verify user exists
            user = self.db.query(User).filter(
                User.id == user_id,
                User.is_active == True
            ).first()
            
            if not user:
                raise AuthenticationException("User not found")
            
            # Blacklist old refresh token
            old_token = TokenBlacklist(
                jti=jti,
                user_id=user_id,
                token_type="refresh",
                expires_at=datetime.utcfromtimestamp(payload.get("exp")),
                reason="refresh"
            )
            self.db.add(old_token)
            
            # Create new tokens
            new_access_token = create_access_token(str(user.id))
            new_refresh_token = create_refresh_token(str(user.id))
            
            self.db.commit()
            
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=15 * 60
            )
            
        except Exception as e:
            if isinstance(e, AuthenticationException):
                raise e
            raise AuthenticationException("Could not refresh token")
    
    async def logout_user(self, access_token: str, refresh_token: Optional[str] = None):
        """Logout user by blacklisting tokens"""
        
        try:
            # Blacklist access token
            access_payload = decode_token(access_token, "access")
            access_jti = access_payload.get("jti")
            user_id = access_payload.get("sub")
            
            if access_jti:
                blacklist_entry = TokenBlacklist(
                    jti=access_jti,
                    user_id=user_id,
                    token_type="access",
                    expires_at=datetime.utcfromtimestamp(access_payload.get("exp")),
                    reason="logout"
                )
                self.db.add(blacklist_entry)
            
            # Blacklist refresh token if provided
            if refresh_token:
                try:
                    refresh_payload = decode_token(refresh_token, "refresh")
                    refresh_jti = refresh_payload.get("jti")
                    
                    if refresh_jti:
                        blacklist_entry = TokenBlacklist(
                            jti=refresh_jti,
                            user_id=user_id,
                            token_type="refresh",
                            expires_at=datetime.utcfromtimestamp(refresh_payload.get("exp")),
                            reason="logout"
                        )
                        self.db.add(blacklist_entry)
                except:
                    pass  # Ignore errors with refresh token
            
            self.db.commit()
            
        except Exception:
            raise AuthenticationException("Could not logout user")
    
    async def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        
        # First check Redis cache
        cache_key = f"blacklist:{jti}"
        cached = await redis_service.get(cache_key)
        
        if cached == "1":
            return True
        elif cached == "0":
            return False
        
        # Check database
        blacklisted = self.db.query(TokenBlacklist).filter(
            TokenBlacklist.jti == jti,
            TokenBlacklist.expires_at > func.now()
        ).first()
        
        # Cache result
        is_blacklisted = blacklisted is not None
        await redis_service.set(cache_key, "1" if is_blacklisted else "0", ex=3600)
        
        return is_blacklisted
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from access token"""
        
        payload = decode_token(token, "access")
        user_id = payload.get("sub")
        jti = payload.get("jti")
        
        if not user_id or not jti:
            raise AuthenticationException("Invalid token")
        
        # Check if token is blacklisted
        if await self.is_token_blacklisted(jti):
            raise AuthenticationException("Token has been revoked")
        
        user = self.db.query(User).filter(
            User.id == user_id,
            User.is_active == True,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            raise AuthenticationException("User not found")
        
        return user
