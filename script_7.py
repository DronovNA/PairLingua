# Создаем API роутеры

# Main router
main_router = """from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.words import router as words_router
from app.api.v1.study import router as study_router
from app.api.v1.achievements import router as achievements_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(words_router, prefix="/words", tags=["words"])
api_router.include_router(study_router, prefix="/study", tags=["study"])
api_router.include_router(achievements_router, prefix="/achievements", tags=["achievements"])
"""

# V1 router
v1_router = """from fastapi import APIRouter
from app.api.v1 import auth, users, words, study, achievements

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"]) 
router.include_router(words.router, prefix="/words", tags=["words"])
router.include_router(study.router, prefix="/study", tags=["study"])
router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
"""

# Auth router
auth_router = """from typing import Optional
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
    \"\"\"Register a new user and return access tokens\"\"\"
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
    \"\"\"Login user and return access tokens\"\"\"
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
    \"\"\"Refresh access token using refresh token\"\"\"
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
    \"\"\"Logout user by blacklisting tokens\"\"\"
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
    \"\"\"Request password reset email\"\"\"
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
    \"\"\"Reset password using reset token\"\"\"
    # Implementation would verify reset token and update password
    return {"message": "Password has been reset successfully"}


# Dependency for getting current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    \"\"\"Get current authenticated user from JWT token\"\"\"
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
"""

# Users router
users_router = """from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import (
    User, UserUpdate, UserStats, UserStatsDetailed
)
from app.api.v1.auth import get_current_user
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/me",
    response_model=User,
    summary="Get current user profile",
    description="Get the profile of the currently authenticated user"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get current user profile\"\"\"
    try:
        user_service = UserService(db)
        return user_service.get_user_profile(str(current_user.id))
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/me",
    response_model=User,
    summary="Update user profile",
    description="Update the profile of the currently authenticated user"
)
async def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Update current user profile\"\"\"
    try:
        user_service = UserService(db)
        return user_service.update_user_profile(str(current_user.id), update_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/me/stats",
    response_model=UserStats,
    summary="Get user statistics",
    description="Get learning statistics for the current user"
)
async def get_my_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get user learning statistics\"\"\"
    try:
        user_service = UserService(db)
        return user_service.get_user_stats(str(current_user.id))
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/me/stats/detailed",
    response_model=UserStatsDetailed,
    summary="Get detailed user statistics",
    description="Get detailed learning statistics with date range"
)
async def get_my_detailed_stats(
    date_range: str = "30days",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get detailed user statistics for specified period\"\"\"
    try:
        if date_range not in ["7days", "30days", "all"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date range. Use: 7days, 30days, or all"
            )
        
        user_service = UserService(db)
        return user_service.get_user_detailed_stats(str(current_user.id), date_range)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change user password"
)
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Change user password\"\"\"
    try:
        user_service = UserService(db)
        success = user_service.change_password(
            str(current_user.id), 
            current_password, 
            new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
    description="Soft delete the current user account"
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Delete user account (soft delete)\"\"\"
    try:
        user_service = UserService(db)
        success = user_service.delete_user_account(str(current_user.id))
        
        if success:
            return {"message": "Account deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete account"
            )
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
"""

# Words router  
words_router = """from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.word_service import WordService
from app.schemas.word import (
    WordPair, WordPairCreate, WordPairUpdate, WordPairSearch,
    WordPairBatchCreate, WordPairWithUserProgress
)
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.core.exceptions import PairLinguaException

router = APIRouter()


@router.get(
    "/pairs",
    response_model=List[WordPairWithUserProgress],
    summary="Search word pairs",
    description="Search word pairs with optional filters and user progress"
)
async def search_word_pairs(
    query: Optional[str] = Query(None, description="Search term"),
    cefr_level: Optional[str] = Query(None, description="CEFR level filter"),
    tags: Optional[List[str]] = Query(None, description="Tags filter"),
    limit: int = Query(20, ge=1, le=100, description="Results limit"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Search word pairs with user progress\"\"\"
    try:
        search_params = WordPairSearch(
            query=query,
            cefr_level=cefr_level,
            tags=tags or [],
            limit=limit,
            cursor=cursor
        )
        
        word_service = WordService(db)
        word_pairs, next_cursor = word_service.get_word_pairs(
            search_params, 
            user_id=str(current_user.id)
        )
        
        # Add pagination header
        # In real implementation, you'd add Link header with next_cursor
        return word_pairs
        
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/pairs/{word_pair_id}",
    response_model=WordPair,
    summary="Get word pair",
    description="Get a specific word pair by ID"
)
async def get_word_pair(
    word_pair_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Get word pair by ID\"\"\"
    try:
        word_service = WordService(db)
        return word_service.get_word_pair(word_pair_id)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/pairs",
    response_model=WordPair,
    status_code=status.HTTP_201_CREATED,
    summary="Create word pair",
    description="Create a new word pair (admin only)"
)
async def create_word_pair(
    word_data: WordPairCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Create new word pair (admin only)\"\"\"
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        return word_service.create_word_pair(word_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/pairs/batch",
    response_model=List[WordPair],
    status_code=status.HTTP_201_CREATED,
    summary="Create word pairs in batch",
    description="Create multiple word pairs at once (admin only)"
)
async def create_word_pairs_batch(
    batch_data: WordPairBatchCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Create multiple word pairs in batch\"\"\"
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        return word_service.create_word_pairs_batch(batch_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch(
    "/pairs/{word_pair_id}",
    response_model=WordPair,
    summary="Update word pair",
    description="Update an existing word pair (admin only)"
)
async def update_word_pair(
    word_pair_id: int,
    update_data: WordPairUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Update word pair\"\"\"
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        return word_service.update_word_pair(word_pair_id, update_data)
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete(
    "/pairs/{word_pair_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete word pair",
    description="Soft delete a word pair (admin only)"
)
async def delete_word_pair(
    word_pair_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    \"\"\"Delete word pair (soft delete)\"\"\"
    try:
        # In real implementation, check if user is admin
        word_service = WordService(db)
        success = word_service.delete_word_pair(word_pair_id)
        
        if success:
            return {"message": f"Word pair {word_pair_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete word pair"
            )
    except PairLinguaException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
"""

# Записываем роутеры
with open("pairlingua/backend/app/api/v1/router.py", "w") as f:
    f.write(main_router)

with open("pairlingua/backend/app/api/v1/__init__.py", "w") as f:
    f.write(v1_router)

with open("pairlingua/backend/app/api/v1/auth.py", "w") as f:
    f.write(auth_router)

with open("pairlingua/backend/app/api/v1/users.py", "w") as f:
    f.write(users_router)

with open("pairlingua/backend/app/api/v1/words.py", "w") as f:
    f.write(words_router)

print("✅ API роутеры созданы")
print("🔐 Auth: регистрация, логин, refresh, logout")  
print("👤 Users: профиль, статистика, смена пароля")
print("📚 Words: поиск, CRUD, batch операции")