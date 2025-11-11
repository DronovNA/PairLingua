from fastapi import APIRouter
from app.api.v1 import auth, users, words, study, achievements

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"]) 
router.include_router(words.router, prefix="/words", tags=["words"])
router.include_router(study.router, prefix="/study", tags=["study"])
router.include_router(achievements.router, prefix="/achievements", tags=["achievements"])
