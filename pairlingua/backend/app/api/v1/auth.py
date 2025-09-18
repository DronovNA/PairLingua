import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Cookie
from fastapi.responses import JSONResponse
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

logger = logging.getLogger(__name__)


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
        logger.info(f"Регистрация пользователя: email={user_data.email}")
        auth_service = AuthService(db)

        # Create user
        await auth_service.register_user(user_data)
        logger.info(f"Пользователь {user_data.email} успешно зарегистрирован")

        # Authenticate and return tokens
        login_data = UserLogin(email=user_data.email, password=user_data.password)
        tokens = await auth_service.authenticate_user(login_data)
        logger.info(f"Пользователь {user_data.email} успешно аутентифицирован")

        return tokens

    except PairLinguaException as e:
        logger.warning(f"Ошибка регистрации {user_data.email}: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error при регистрации {user_data.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", summary="User login", description="Authenticate user and set tokens in httpOnly cookies")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        tokens = await auth_service.authenticate_user(credentials)

        response = JSONResponse(content={"message": "Login successful"})
        # Установить куки access token
        response.set_cookie(
            key="access_token",
            value=tokens.access_token,
            httponly=True,
            samesite="lax",
            secure=False,       # ставьте True в проде с https
            max_age=15 * 60,   # 15 мин
            path="/",
        )
        # Установить куки refresh token
        response.set_cookie(
            key="refresh_token",
            value=tokens.refresh_token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=7 * 24 * 3600,  # 7 дней
            path="/refresh"
        )
        return response

    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")


@router.post("/refresh", summary="Refresh access token", description="Refresh JWT tokens in httpOnly cookies")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    auth_service = AuthService(db)
    try:
        new_tokens = await auth_service.refresh_token(refresh_token)

        response = JSONResponse(content={"message": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=new_tokens.access_token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=15 * 60,
            path="/"
        )
        response.set_cookie(
            key="refresh_token",
            value=new_tokens.refresh_token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=7 * 24 * 3600,
            path="/refresh"
        )
        return response

    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception:
        raise HTTPException(status_code=401, detail="Token refresh failed")


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Revoke access and refresh tokens"
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    refresh_token_param: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Logout user by blacklisting tokens"""
    try:
        auth_service = AuthService(db)
        await auth_service.logout_user(credentials.credentials, refresh_token_param)
        
        return {"message": "Successfully logged out"}
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception:
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
    _reset_data: PasswordReset,
    _db: Session = Depends(get_db)
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
    _reset_data: PasswordResetConfirm,
    _db: Session = Depends(get_db)
):
    """Reset password using reset token"""
    # Implementation would verify reset token and update password
    return {"message": "Password has been reset successfully"}


# Dependency for getting current user
async def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Missing token")
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(access_token)
        return user
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
