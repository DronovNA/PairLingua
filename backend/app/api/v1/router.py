from fastapi import APIRouter
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
