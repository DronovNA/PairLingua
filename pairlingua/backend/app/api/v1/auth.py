from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserRegister, UserLogin, Token, TokenRefresh, 
    TokenRefreshResponse, PasswordReset, PasswordResetConfirm
)
from app.core.exceptions import PairLinguaException

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/register", 
    response_model=Token,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password"
)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user and return access tokens"""
    try:
        auth_service = AuthService(db)
        
        # Create user
        user = await auth_service.register_user(user_data)
        
        # Authenticate and return tokens
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        tokens = await auth_service.authenticate_user(login_data)
        
        return tokens
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="User login",
    description="Authenticate user with email and password, return JWT tokens"
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """Login user and return access tokens"""
    try:
        auth_service = AuthService(db)
        tokens = await auth_service.authenticate_user(credentials)
        return tokens
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Refresh access token",
    description="Use refresh token to get new access token"
)
async def refresh_token(
    token_data: TokenRefresh,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        auth_service = AuthService(db)
        new_tokens = await auth_service.refresh_token(token_data.refresh_token)
        
        return TokenRefreshResponse(
            access_token=new_tokens.access_token,
            refresh_token=new_tokens.refresh_token,
            expires_in=new_tokens.expires_in
        )
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Revoke access and refresh tokens"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    refresh_token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Logout user by blacklisting tokens"""
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(credentials.credentials, refresh_token)
        
        return {"message": "Successfully logged out"}
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email (if email exists)"
)
async def forgot_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """Request password reset email"""
    # Always return success for security (don't reveal if email exists)
    return {"message": "If email exists, password reset instructions have been sent"}


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset password using reset token"
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    # Implementation would verify reset token and update password
    return {"message": "Password has been reset successfully"}


# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user from JWT token"""
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
